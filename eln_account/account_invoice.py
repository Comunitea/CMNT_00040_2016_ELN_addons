# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
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

import decimal_precision as dp

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def _received_check(self, cr, uid, ids, name, args, context=None):
        res = {}

        for inv in self.browse(cr, uid, ids, context=context):
            res[inv.id] = False
            if inv.move_id and inv.move_id.line_id:
                for line in inv.move_id.line_id:
                    if line.received_check:
                        res[inv.id] = True
        return res

    #Si queremos que el store sea True es mejor usar este método. Lo dejo hecho por si lo queremos usar así
    #def _received_check(self, cr, uid, ids, name, args, context=None):
    #    res = {}
    #
    #    acc_obj = self.pool.get('account.move.line')
    #    inv_ids = []
    #    for acc_id in acc_obj.browse(cr, uid, ids):
    #        if acc_id.invoice:
    #            inv_ids.append(acc_id.invoice.id)
    #            
    #    inv_ids = list(set(inv_ids))
    #    
    #    for inv in self.browse(cr, uid, inv_ids, context=context):
    #        res[inv.id] = False
    #        if inv.move_id and inv.move_id.line_id:
    #            for line in inv.move_id.line_id:
    #                if line.received_check:
    #                    res[inv.id] = True
    #    return res
    
    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()

    def _get_invoice_from_line(self, cr, uid, ids, context=None):
        move = {}
        for line in self.pool.get('account.move.line').browse(cr, uid, ids, context=context):
            if line.reconcile_partial_id:
                for line2 in line.reconcile_partial_id.line_partial_ids:
                    move[line2.move_id.id] = True
            if line.reconcile_id:
                for line2 in line.reconcile_id.line_id:
                    move[line2.move_id.id] = True
        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return invoice_ids

    def _get_invoice_from_reconcile(self, cr, uid, ids, context=None):
        move = {}
        for r in self.pool.get('account.move.reconcile').browse(cr, uid, ids, context=context):
            for line in r.line_partial_ids:
                move[line.move_id.id] = True
            for line in r.line_id:
                move[line.move_id.id] = True

        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return invoice_ids

    def _amount_residual(self, cr, uid, ids, name, args, context=None):
        result = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            checked_partial_rec_ids = []
            result[invoice.id] = 0.0
            if invoice.move_id:
                for move_line in invoice.move_id.line_id:
                    if move_line.account_id.type in ('receivable','payable'):
                        if move_line.reconcile_partial_id:
                            partial_reconcile_id = move_line.reconcile_partial_id.id
                            if partial_reconcile_id in checked_partial_rec_ids:
                                continue
                            checked_partial_rec_ids.append(partial_reconcile_id)
                        result[invoice.id] += move_line.amount_residual_currency
        return result

    _columns = {
        'received_check': fields.function(_received_check, method=True, store=False, type='boolean', string='Received check', help="To write down that a check in paper support has been received, for example."),
        #Si queremos que el store sea True es mejor usar este método. Lo dejo hecho por si lo queremos usar así
        #'received_check' : fields.function(_received_check, method=True,
        #        type='boolean', string='Received check',
        #        help="To write down that a check in paper support has been received, for example.",
        #        store={
        #           'account.move.line': (lambda self, cr, uid, ids, context=None: ids, None, 20),
        #        }),
        
        'residual': fields.function(_amount_residual, digits_compute=dp.get_precision('Account'), string='Balance',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line','move_id'], 50),
                'account.invoice.tax': (_get_invoice_tax, None, 50),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 50),
                'account.move.line': (_get_invoice_from_line, None, 50),
                'account.move.reconcile': (_get_invoice_from_reconcile, None, 50),
            },
            help="Remaining amount due."),
    }

    def _refund_cleanup_lines(self, cr, uid, lines):
        """ugly function to map all fields of account.invoice.line when creates refund invoice"""
        res = super(account_invoice, self)._refund_cleanup_lines(cr, uid, lines)

        for line in res:
            if 'tax_id' in line[2]:
                line[2]['tax_id'] = line[2]['tax_id'] and line[2]['tax_id'][0] or False

        return res
    
account_invoice()

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    def uos_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, address_invoice_id=False, currency_id=False, context=None, company_id=None):
        """
        Modificamos para no permitir poner cualquier tipo de unidad en la linea de factura.
        Ahora solo aceptará alguna que pertenezca a la misma categoria que la unidad de medida por defecto del producto.
        """
        if context is None:
            context = {}
            
        update_res = False
        
        if product and uom:
            prod = self.pool.get('product.product').browse(cr, uid, product, context=context)
            prod_uom = self.pool.get('product.uom').browse(cr, uid, uom, context=context)
            if prod.uom_id.category_id.id != prod_uom.category_id.id:
                update_res = True
                uom = (prod.uos_id and prod.uos_id.id) or (prod.uom_id and prod.uom_id.id) or False
            
        res = super(account_invoice_line, self).uos_id_change(cr, uid, ids, product, uom, qty, name, type, partner_id, fposition_id, price_unit, address_invoice_id, currency_id, context, company_id)

        if update_res:
            res['value']['uos_id'] = uom or False

        return res

account_invoice_line()