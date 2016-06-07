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

from openerp.osv import orm


class StockMove(orm.Model):
    _inherit = 'stock.move'

    def _get_price_unit_invoice(self, cr, uid, move_line, type, context=None):
        """
        Si el tipo de factura es de entrada y no tiene una compra asociada,
        obtenemos el precio de la tarifa del partner.
        """
        if context is None:
            context = {}
        if type in ('in_invoice', 'in_refund'):
            if move_line.location_id.usage in ['supplier', 'transit'] and \
                    not move_line.purchase_line_id:
                pricelist_obj = self.pool.get("product.pricelist")
                pricelist = move_line.picking_id.partner_id.\
                    property_product_pricelist_purchase.id
                price = pricelist_obj.price_get(cr, uid, [pricelist],
                                                move_line.product_id.id,
                                                move_line.product_uom_qty,
                                                move_line.partner_id.id,
                                                {
                                                'uom': move_line.
                                                    product_uom.id,
                                                'date': move_line.date,
                                                })[pricelist]
                if price:
                    # Escribimos el precio unitario, para que en el super
                    # al entrar por el mismo if, lo devuelva.
                    move_line.write({'price_unit': price})
        else:
            # Escribir el partner en el movimiento para que el super
            # sea capaz de calcularlo
            if not move_line.procurement_id.sale_line_id and \
                    not move_line.partner_id:
                part_id = move_line.picking_id.partner_id and \
                    move_line.picking_id.partner_id.id or False
                move_line.write({'partner_id': part_id})
        return super(StockMove, self)._get_price_unit_invoice(cr, uid,
                                                              move_line,
                                                              type,
                                                              context=context)

    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type,
                               context=None):
        res = super(StockMove, self).\
            _get_invoice_line_vals(cr, uid, move, partner, inv_type,
                                   context=context)
        if inv_type in ['in_invoice', 'in_refund']:
            if move.product_uos and move.product_uom_qty and \
                    move.product_uos.id != move.product_uom.id:
                uos_coeff = move.product_uos_qty / move.product_uom_qty
                if uos_coeff:
                    res['price_unit'] = res['price_unit'] / uos_coeff
        if inv_type in ['out_invoice', 'out_refund']:
            if not move.procurement_id or \
                    (move.procurement_id and
                     not move.procurement_id.sale_line_id) and \
                    move.product_uos.id != move.product_uom.id and\
                    move.product_uom_qty:
                uos_coeff = move.product_uos_qty / move.product_uom_qty
                if uos_coeff:
                    res['price_unit'] = res['price_unit'] / uos_coeff
        return res
