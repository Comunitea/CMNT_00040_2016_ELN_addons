# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
import time

class rappel(osv.osv):
    _name = 'rappel'
    _columns = {
        'name': fields.char('Name', size=60, required=True,readonly=True,states={'draft': [('readonly', False)]}),
        'date_start': fields.date('Start Date', required=True,readonly=True,states={'draft': [('readonly', False)]}),
        'date_stop': fields.date('Stop Date', required=True,readonly=True,states={'draft': [('readonly', False)]}),
        'line_ids': fields.one2many('rappel.line','rappel_id', 'Rappel Lines',readonly=True,states={'draft': [('readonly', False)]}),
        'state' : fields.selection([('draft','Draft'),('open','Open'),('cancel','Canceled'),('done','Done')],'State',readonly=True),
        'journal_id': fields.many2one('account.journal', 'Refund Journal', domain="[('type','=','sale_refund')]", required=True,readonly=True,states={'draft': [('readonly', False)]}),
    }

    _defaults = {
        'state': lambda *args: 'draft'
    }
  
    def action_open(self, cr, uid, ids, *args):
        return True

    def action_done(self, cr, uid, ids, group=True, type='out_refund', context=None):
        # need to make perfect checking
        # remaining to check sale condition
        # need Improvement
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        partner_obj = self.pool.get('res.partner')
        for rappel in self.browse(cr, uid, ids):
            for line in rappel.line_ids:
                qty = 0.0
                price_unit = 0.0
                query_params = (rappel.id,rappel.date_start,rappel.date_stop,)
                query_cond = ""
                if line.condition_product_id:
                    query_cond += " AND inv_line.product_id = %s"
                    query_params += (line.condition_product_id.id,)
                if line.condition_category_id:
                    query_cond += " AND prod_template.categ_id = %s"
                    query_params += (line.condition_category_id.id,)
                cr.execute("""
                 SELECT max(invoice.id), sum(inv_line.quantity), sum(inv_line.price_subtotal)
                 FROM account_invoice invoice
                  LEFT JOIN res_partner partner ON (invoice.partner_id = partner.id)
                  LEFT JOIN account_invoice_line inv_line ON (invoice.id = inv_line.invoice_id)
                  LEFT JOIN product_product product ON (inv_line.product_id = product.id)
                  LEFT JOIN product_template prod_template ON (product.product_tmpl_id = prod_template.id)
                 WHERE partner.rappel_id = %s
                  AND (invoice.date_invoice BETWEEN %s AND %s)
                  AND invoice.type = 'out_invoice'
                  AND invoice.state in ('open','paid')
                 """ + query_cond + """
                  GROUP BY partner.id
                """, query_params)
                
                for res in cr.fetchall():
                    if (line.qty_amount == 'qty' and res[1] >= line.condition_qty) or (line.qty_amount == 'amount' and res[2] >= line.condition_amount):
                        if line.qty_amount == 'qty':
                            qty = res[1] * line.discount / 100
                            price_unit = res[2] / res[1]
                        elif line.qty_amount == 'amount':
                            price_unit = res[2] * line.discount / 100
                            qty = 1.0

                        invoice_record = invoice_obj.browse(cr, uid, res[0], context)
                        new_invoice = {}
                        partner_id = invoice_record.partner_id.id
                        fpos = partner_obj.browse(cr, uid, partner_id).property_account_position
                        new_invoice.update({
                            'partner_id': partner_id,
                            'journal_id': rappel.journal_id.id,
                            'account_id': invoice_record.partner_id.property_account_receivable.id,
                            'address_contact_id': invoice_record.address_contact_id.id,
                            'address_invoice_id': invoice_record.address_invoice_id.id,
                            'type': 'out_refund',
                            'date_invoice': time.strftime('%Y-%m-%d'),
                            'state': 'draft',
                            'number': False,
                            'fiscal_position': fpos and fpos.id or False
                        })
                        invoice_id = invoice_obj.create(cr, uid, new_invoice,context=context)
                        account_id = line.condition_product_id and (line.condition_product_id.property_account_income and line.condition_product_id.property_account_income.id or (line.condition_product_id.categ_id.property_account_income_categ and line.condition_product_id.categ_id.property_account_income_categ.id or False)) or (line.condition_category_id.property_account_income_categ and line.condition_category_id.property_account_income_categ.id or False)
                        if not account_id:
                            account_id = rappel.journal_id.default_debit_account_id and rappel.journal_id.default_debit_account_id.id or False,
                            if not account_id:
                                raise osv.except_osv(_('No account found'),_("OpenERP was not able to find an income account to put on the refund invoice line. Configure the default debit account on the selected refund journal."))
                        invoice_line_id = invoice_line_obj.create(cr, uid,  {
                               'name': line.name,
                               'invoice_id': invoice_id,
                               'product_id': line.condition_product_id and line.condition_product_id.id or False,
                               'uos_id': line.condition_product_id and line.condition_product_id.uom_id.id or False,
                               'account_id': account_id,
                               'price_unit': price_unit,
                               'quantity': qty })
                    
        return True


rappel()

class rappel_line(osv.osv):
    _name = 'rappel.line'
    _columns = {
        'name': fields.char('Name', size=60, required=True),
        'sequence': fields.integer('Sequence', required=True),
        'condition_category_id': fields.many2one('product.category', 'Category'),
        'condition_product_id' : fields.many2one('product.product', 'Product'),
        'qty_amount': fields.selection([('qty', 'By Qty.'),('amount', 'By Amount')], 'Settled', required=True),
        'condition_amount' : fields.float('Min. Amount', required=True),
        'condition_qty' : fields.float('Min. Quantity', required=True),
        'discount' : fields.float('Discount (%)'),
        'rappel_id': fields.many2one('rappel', 'Rappel'),
    }
    _defaults = {
        'sequence': lambda *a: 5,
        'condition_amount': lambda *a: 1.0,
        'condition_qty': lambda *a: 1.0
    }

rappel_line()