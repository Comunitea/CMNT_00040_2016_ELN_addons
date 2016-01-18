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

from openerp.osv import fields, osv, orm
from tools.translate import _

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

    _columns = {
        'received_check': fields.function(_received_check, method=True, store=False, type='boolean', string='Received check', help="To write down that a check in paper support has been received, for example."),
        #Si queremos que el store sea True es mejor usar este método. Lo dejo hecho por si lo queremos usar así
        #'received_check' : fields.function(_received_check, method=True,
        #        type='boolean', string='Received check',
        #        help="To write down that a check in paper support has been received, for example.",
        #        store={
        #           'account.move.line': (lambda self, cr, uid, ids, context=None: ids, None, 20),
        #        }),
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
