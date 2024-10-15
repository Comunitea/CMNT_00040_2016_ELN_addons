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
from odoo import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _get_price_unit_invoice(self, move_line, type):
        """
        Si el tipo de factura es de entrada y no tiene una compra asociada,
        obtenemos el precio de la tarifa del partner.
        """
        if type in ('in_invoice', 'in_refund') and not move_line.purchase_line_id:
            loc = move_line.location_id if type == 'in_invoice' else move_line.location_dest_id
            if loc.usage in ('supplier', 'transit'):
                pricelist = move_line.picking_id.partner_id.property_product_pricelist_purchase
                price = False
                if pricelist:
                    uom = move_line.product_uom.id
                    date_price = move_line.date
                    price = pricelist.with_context(uom=uom,date=date_price).price_get(
                        move_line.product_id.id, move_line.product_uom_qty, partner=move_line.partner_id.id)[pricelist.id]
                if price:
                    move_line.write({'price_unit': price}) # Escribimos el precio para que al llamar al super lo devuelva
        else:
            if not move_line.procurement_id.sale_line_id and not move_line.partner_id:
                # Escribimos el partner en el movimiento para que el super sea capaz de calcularlo
                move_line.write({'partner_id': move_line.picking_id.partner_id.id})
        return super(StockMove, self)._get_price_unit_invoice(move_line, type)


    @api.model
    def _get_invoice_line_vals(self, move, partner, inv_type):
        res = super(StockMove, self)._get_invoice_line_vals(move, partner, inv_type)
        if inv_type in ('in_invoice', 'in_refund'):
            if move.product_uos and move.product_uom_qty and \
                    move.product_uos.id != move.product_uom.id:
                uos_coeff = move.product_uos_qty / move.product_uom_qty
                if uos_coeff:
                    res['price_unit'] = res['price_unit'] / uos_coeff
        if inv_type in ('out_invoice', 'out_refund'):
            if (not move.procurement_id or (move.procurement_id and not move.procurement_id.sale_line_id)) and \
                    move.product_uos and move.product_uom_qty and \
                    move.product_uos.id != move.product_uom.id:
                uos_coeff = move.product_uos_qty / move.product_uom_qty
                if uos_coeff:
                    res['price_unit'] = res['price_unit'] / uos_coeff
        return res

