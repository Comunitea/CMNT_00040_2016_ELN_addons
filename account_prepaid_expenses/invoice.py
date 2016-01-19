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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class account_invoice_line(models.Model):

    _inherit = "account.invoice.line"

    prepaid_expense_amount = fields.Float('Prepaid exp. amount',
                                          digits_compute=dp.
                                          get_precision('Account'))
    prepaid_expense_amount_untaxed = fields.Float('Prepaid exp. untax amount',
                                                  digits_compute=dp.
                                                  get_precision('Account'))

    @api.model
    def move_line_get_item(self, line):
        res = super(account_invoice_line, self).move_line_get_item(line)
        res['prepaid_expense_amount_untaxed'] = \
            (line.prepaid_expense_amount_untaxed or 0.0)

        return res


class account_invoice(models.Model):

    _inherit = "account.invoice"

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(account_invoice, self).line_get_convert(line, part, date)
        res['prepaid_expense_amount_untaxed'] = \
            line.get('prepaid_expense_amount_untaxed', 0.0)
        res['taxes'] = line.get('taxes', [])
        return res

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        new_lines = []
        obj = self[0]
        for line in move_lines:
            if (line[2].get('prepaid_expense_amount_untaxed') and
                    line[2].get('taxes')):
                for tax in line[2]['taxes']:
                    new_dict = dict(line[2])
                    if obj.type in ('out_invoice', 'in_invoice'):
                        new_dict['tax_amount'] = \
                            new_dict['prepaid_expense_amount_untaxed'] * \
                            tax.tax_sign
                    else:
                        new_dict['tax_amount'] = \
                            new_dict['prepaid_expense_amount_untaxed'] * \
                            tax.ref_tax_sign
                    new_dict['debit'] = 0.0
                    new_dict['credit'] = 0.0
                    new_lines.append((0, 0, new_dict))

        res = super(account_invoice, self).\
            finalize_invoice_move_lines(move_lines)
        res.extend(new_lines)

        return res


class account_invoice_tax(models.Model):

    _inherit = "account.invoice.tax"

    @api.v8
    def compute(self, invoice):
        tax_grouped = super(account_invoice_tax, self).compute(invoice)

        currency = invoice.currency_id.\
            with_context(invoice=invoice.date_invoice or fields.Date.
                         context_today(self))
        company_currency = invoice.company_id.currency_id

        for line in invoice.invoice_line:
            if line.prepaid_expense_amount:
                for tax in line.invoice_line_tax_id.\
                    compute_all(0.0, line.quantity, line.product_id,
                                invoice.partner_id)['taxes']:
                    tax['price_unit'] = 0.0
                    val = {}
                    val['invoice_id'] = invoice.id
                    val['name'] = _("Prepaid Expenses")
                    val['amount'] = line.prepaid_expense_amount
                    val['manual'] = False
                    val['sequence'] = tax['sequence']
                    val['base'] = 0.0

                    if invoice.type in ('out_invoice', 'in_invoice'):
                        val['base_code_id'] = False
                        val['tax_code_id'] = tax['tax_code_id']
                        val['base_amount'] = 0.0
                        val['tax_amount'] = \
                            currency.compute(val['amount'] * tax['tax_sign'],
                                             company_currency, round=False)
                        val['account_id'] = (tax['account_collected_id'] or
                                             line.account_id.id)
                    else:
                        val['base_code_id'] = False
                        val['tax_code_id'] = tax['ref_tax_code_id']
                        val['base_amount'] = 0.0
                        val['tax_amount'] = \
                            currency.compute(val['amount'] *
                                             tax['ref_tax_sign'],
                                             company_currency, round=False)
                        val['account_id'] = (tax['account_paid_id'] or
                                             line.account_id.id)

                    key = (val['tax_code_id'], False, val['account_id'])
                    if key not in tax_grouped:
                        tax_grouped[key] = val
                    else:
                        tax_grouped[key]['amount'] += val['amount']
                        tax_grouped[key]['base'] += val['base']
                        tax_grouped[key]['base_amount'] += val['base_amount']
                        tax_grouped[key]['tax_amount'] += val['tax_amount']

        tax_grouped1 = {}
        for t in tax_grouped:
            if tax_grouped[t]['base_amount'] or tax_grouped[t]['tax_amount']:
                tax_grouped[t]['base'] = currency.round(tax_grouped[t]['base'])
                tax_grouped[t]['amount'] = currency.\
                    round(tax_grouped[t]['amount'])
                tax_grouped[t]['base_amount'] = currency.\
                    round(tax_grouped[t]['base_amount'])
                tax_grouped[t]['tax_amount'] = currency.\
                    round(tax_grouped[t]['tax_amount'])

                tax_grouped1[t] = tax_grouped[t]
        return tax_grouped1
