# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-TODAY
#    Pexego Sistemas Informáticos (http://www.pexego.es) All Rights Reserved
#    $Omar Castiñeira Saavedra$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
import time
from openerp import models, api, _
#from openerp import fields as fields2

class account_invoice_line(osv.osv):

    _inherit = "account.invoice.line"

    _columns = {
        'prepaid_expense_amount': fields.float('Prepaid exp. amount', digits_compute=dp.get_precision('Account')),
        'prepaid_expense_amount_untaxed': fields.float('Prepaid exp. untaxed amount', digits_compute=dp.get_precision('Account'))
    }

    def move_line_get_item(self, cr, uid, line, context=None):
        res = super(account_invoice_line, self).move_line_get_item(cr, uid, line, context=context)
        res['prepaid_expense_amount_untaxed'] = (line.prepaid_expense_amount_untaxed or 0.0)

        return res

account_invoice_line()

class account_invoice(osv.osv):

    _inherit = "account.invoice"

    def line_get_convert(self, cr, uid, x, part, date, context=None):
        res = super(account_invoice, self).line_get_convert(cr, uid, x, part, date, context=context)
        res['prepaid_expense_amount_untaxed'] = x.get('prepaid_expense_amount_untaxed', 0.0)
        res['taxes'] = x.get('taxes', [])
        return res

    def finalize_invoice_move_lines(self, cr, uid, invoice_browse, move_lines):
        new_lines = []
        for line in move_lines:
            if line[2].get('prepaid_expense_amount_untaxed') and line[2].get('taxes'):
                new_dict = dict(line[2])
                new_dict['tax_amount'] = new_dict['prepaid_expense_amount_untaxed']
                new_dict['debit'] = 0.0
                new_dict['credit'] = 0.0
                new_lines.append((0,0,new_dict))

        res = super(account_invoice, self).finalize_invoice_move_lines(cr, uid, invoice_browse, move_lines)
        res.extend(new_lines)

        return res

class account_invoice_tax(models.Model):

    _inherit = "account.invoice.tax"

    @api.v8
    def compute(self, inv):
        tax_grouped = super(account_invoice_tax, self).compute(inv)
        tax_obj = self.env['account.tax']
        cur_obj = self.env['res.currency']
        cur = inv.currency_id
        company_currency = inv.company_id.currency_id.id

        for line in inv.invoice_line:
            if line.prepaid_expense_amount:
                for tax in tax_obj.compute_all(line.invoice_line_tax_id, 0.0, line.quantity, inv.address_invoice_id.id, line.product_id, inv.partner_id)['taxes']:
                    tax['price_unit'] = 0.0
                    val={}
                    val['invoice_id'] = inv.id
                    val['name'] = _("Prepaid Expenses")
                    val['amount'] = line.prepaid_expense_amount
                    val['manual'] = False
                    val['sequence'] = tax['sequence']
                    val['base'] = 0.0

                    if inv.type in ('out_invoice','in_invoice'):
                        val['base_code_id'] = False
                        val['tax_code_id'] = tax['tax_code_id']
                        val['base_amount'] = 0.0
                        val['tax_amount'] = cur_obj.compute(inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                        val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    else:
                        val['base_code_id'] = False
                        val['tax_code_id'] = tax['ref_tax_code_id']
                        val['base_amount'] = 0.0
                        val['tax_amount'] = cur_obj.compute(inv.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                        val['account_id'] = tax['account_paid_id'] or line.account_id.id

                    key = (val['tax_code_id'], False, val['account_id'])
                    if not key in tax_grouped:
                        tax_grouped[key] = val
                    else:
                        tax_grouped[key]['amount'] += val['amount']
                        tax_grouped[key]['base'] += val['base']
                        tax_grouped[key]['base_amount'] += val['base_amount']
                        tax_grouped[key]['tax_amount'] += val['tax_amount']

        tax_grouped1 = {}
        for t in tax_grouped:
            if tax_grouped[t]['base_amount'] or tax_grouped[t]['tax_amount']:
                tax_grouped[t]['base'] = cur.round(tax_grouped[t]['base'])
                tax_grouped[t]['amount'] = cur.round(tax_grouped[t]['amount'])
                tax_grouped[t]['base_amount'] = cur.round(tax_grouped[t]['base_amount'])
                tax_grouped[t]['tax_amount'] = cur.round(tax_grouped[t]['tax_amount'])
                tax_grouped1[t] = tax_grouped[t]
        return tax_grouped1
