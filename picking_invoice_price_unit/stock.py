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

from openerp.osv import orm, fields

# POST-MIGRATION: Se hereda en stock.move el metodo, la demas funcionalidad ya esta
# implementada en odoo 8. solo migrtamos la parte de coger el precio de la tarifa del proveedor
# cuando no tiene pedido de compra asociado. ya que por defecto devuelve el precio_unit del movimiento.
# class stock_picking(osv.osv):
#     _inherit = 'stock.picking'

#     def _get_price_unit_invoice(self, cursor, user, move_line, type, context=None):

#         if context is None:
#             context = {}
#         price = False
#         product_uom_obj = self.pool.get('product.uom')

#         #Si el movimiento no tiene pedido de compra o venta asociado buscamos el precio en la 
#         #tarifa de precios del cliente/proveedor o en el producto
#         #Si tiene pedido de compra se obtiene el precio del pedido de compra
#         #Si tiene pedido de venta se obtiene el precio del pedido de venta
#         if not (move_line.sale_line_id and move_line.sale_line_id.product_id.id == move_line.product_id.id) and \
#            not (move_line.purchase_line_id and move_line.purchase_line_id.product_id.id == move_line.product_id.id): # Si el movimiento no tiene pedido de compra o venta asociado
#             if move_line.picking_id.address_id:
#                 if type in ('out_invoice', 'out_refund'):
#                     pricelist = move_line.picking_id.address_id.partner_id.property_product_pricelist and move_line.picking_id.address_id.partner_id.property_product_pricelist.id or False 
#                 else:
#                     pricelist = move_line.picking_id.address_id.partner_id.property_product_pricelist_purchase and move_line.picking_id.address_id.partner_id.property_product_pricelist_purchase.id or False
#                 if pricelist:
#                     price = self.pool.get('product.pricelist').price_get(cursor, user, [pricelist],
#                             move_line.product_id.id, move_line.product_qty or 1.0, move_line.picking_id.address_id.partner_id.id, {
#                                 'uom': move_line.product_id.uom_id.id,
#                                 'date': move_line.date,
#                                 })[pricelist]
#                 else:
#                     price = False
#             else:
#                 price = False
#             if not price: # Si no tiene precio en tarifa se obtiene del producto
#                 if type in ('in_invoice', 'in_refund'):
#                     # Take the user company and pricetype
#                     context['currency_id'] = move_line.company_id.currency_id.id
#                     price = move_line.product_id.price_get('standard_price', context=context)[move_line.product_id.id]
#                 else:
#                     price = move_line.product_id.list_price
#         elif move_line.sale_line_id and move_line.sale_line_id.product_id.id == move_line.product_id.id: #Tiene pedido de venta
#             price = move_line.sale_line_id.price_unit
#             from_uom_id = move_line.sale_line_id.product_uom.id
#             to_uom_id = move_line.product_id.uom_id.id
#             price = product_uom_obj._compute_price(cursor, user, from_uom_id, price, to_uom_id)
#         elif move_line.purchase_line_id and move_line.purchase_line_id.product_id.id == move_line.product_id.id: #Tiene pedido de compra
#             price = move_line.purchase_line_id.price_unit
#             from_uom_id = move_line.purchase_line_id.product_uom.id
#             to_uom_id = move_line.product_id.uom_id.id
#             price = product_uom_obj._compute_price(cursor, user, from_uom_id, price, to_uom_id)
#         else: #No debería pasar nunca por aquí
#             print 'No debería estar pasando por aquí.'
#             return super(stock_picking, self)._get_price_unit_invoice(cursor, user, move_line, type)

#         #Hasta aqui tenemos el precio unitario para la unidad de medida del producto
#         #Ahora decidiremos si lo convertimos a la unidad de venta
#         uom_id = move_line.product_id.uom_id.id
#         uos_id = move_line.product_id.uos_id and move_line.product_id.uos_id.id or False
#         move_uos_id = move_line.product_uos and move_line.product_uos.id or False
#         coeff = move_line.product_id.uos_coeff
#         if move_uos_id and move_uos_id != uom_id: # Si hay unidad de venta convertimos porque será la usada en la factura
#             if move_uos_id == uos_id and coeff != 0: # Si coincide con la del producto usamos el coeficiente del producto
#                 price_unit = price / coeff
#                 price = price_unit
#             else: #Si la unidad no coincide con la del producto o el coeficiente no esta fijado, intentamos convertir entre unidades de la misma categoria
#                 from_uom_id = uom_id
#                 to_uom_id = move_uos_id
#                 price = product_uom_obj._compute_price(cursor, user, from_uom_id, price, to_uom_id)
#         return price


class stock_move(orm.Model):
    _inherit = 'stock.move'

    def _get_price_unit_invoice(self, cr, uid, move_line, type, context=None):
        """ 
        Si el tipo de factura es de entrada y no tiene una compra asociada,
        obtenemos el precio de la tarifa del partner.
        """
        if context is None:
            context = {}

        if type in ('in_invoice', 'in_refund'):
            if not (move_line.procurement_id and move_line.procuremennt_id.purchase_line_id and \
                    move_line.procurement_id.purchase_line_id.product_id.id == move_line.product_id.id):
                pricelist_obj = self.pool.get("product.pricelist")
                pricelist = move_line.picking_id.partner_id.property_product_pricelist_purchase.id
                price = pricelist_obj.price_get(cr, uid, [pricelist],
                        move_line.product_id.id, move_line.product_uom_qty, move_line.partner_id.id, {
                            'uom': move_line.product_uom.id,
                            'date': move_line.date,
                            })[pricelist]
                if price:# Escribimos el precio unitario, para que en el super al entrar por el mismo if, lo devuelva.
                    move_line.write({'price_unit': price})
        else:  # Escribir el partner en el movimiento para que el super sea capaz de calcularlo
            if not (move_line.procurement_id and move_line.procurement_id.sale_line_id and \
                    move_line.procurement_id.sale_line_id.product_id.id == move_line.product_id.id):
                move_line.write({'partner_id': move.picking_id and move.picking_id.partner_id and move.picking_id.partner_id.id or False}) 
        return super(stock_move, self)._get_price_unit_invoice(cr, uid, move_line, type, context=context)