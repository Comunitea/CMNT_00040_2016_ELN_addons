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
from openerp import models, fields, api


class StockPicking(models.Model):

    _inherit = 'stock.picking'
    _order = 'id desc'

    address = fields.Char('Address',
                          compute='_get_address',
                          search='_search_address')

    @api.multi
    def _get_address(self):
        for pick in self:
            pick.address = pick.partner_id.street + ' ' + \
                pick.partner_id.street2

    @api.model
    def _search_address(self, operator, operand):
        part = self.env['res.partner'].search(
            ['|',
             ('street', operator, operand),
             ('street2', operator, operand)])
        return [('partner_id', 'in', part._ids)]


class StockIncoterms(models.Model):
    _inherit = "stock.incoterms"

    #  Ponemos el campo name como traducible
    name = fields.Char(translate=True)


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def onchange_quantity(self, product_id, product_qty,
                          product_uom, product_uos):
        """
        Modificamos para que solo permita en unidad de medida la que tiene
            el producto como uom o como uom_po
        Modificamos para que solo permita en unidad de venta la que tiene el
            producto asignada
        Con todo esto evitamos sobre todo problemas en precios en facturas
            (_get_price_unit_invoice)
        """
        if product_id:
            product = self.env['product.product'].browse(product_id)
            uos = product.uos_id and product.uos_id.id or False
            uom = product.uom_id and product.uom_id.id or False
            uom_po = product.uom_po_id and product.uom_po_id.id or False
            if product_uom not in (uom, uom_po):
                product_uom = uom
            if product_uos:
                product_uos = uos
        res = super(StockMove, self).onchange_quantity(product_id,
                                                       product_qty,
                                                       product_uom,
                                                       product_uos)

        res['value']['product_uom'] = product_uom
        res['value']['product_uos'] = product_uos

        # Cuando se abre una linea existente para editar, si ya habia pasado
        # por aqui va a usar el dominio del articulo anterior.
        # Si es un inconveniente eliminar todo lo que está en el if
        if product_id:
            res['domain'] = {'product_uom': [('id', 'in', (uom, uom_po))],
                             'product_uos': [('id', 'in', (uos,))]}
        else:
            res['domain'] = {'product_uom': [], 'product_uos': []}
        return res

    @api.multi
    def unlink(self):
        res = False
        for move in self:
            if move.state == 'cancel' and move.picking_id.pack_operation_ids:
                move.picking_id.pack_operation_ids.unlink()  # Delete move
            else:
                res = super(StockMove, self).unlink()
        return res
