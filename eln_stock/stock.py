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

    @api.model
    def _prepare_values_extra_move(self, op, product, remaining_qty):  
        res = super(StockPicking, self).\
            _prepare_values_extra_move(op, product, remaining_qty)
        """
        Si no tenemos la UdV la obtenemos del movimiento relacionado o del producto si la tiene
        En caso de no poder obtenerla, no la establecemos (Se podria pasar la UdM como UdV),
        pero no se considera necesario.
        """
        if not res.get('uos_id', False) and \
            ((op.linked_move_operation_ids and op.linked_move_operation_ids[0].move_id.product_uos) or op.product_id.uos_id):
            t_uom = self.env['product.uom']
            uom_id = op.product_uom_id.id
            uos_id = (op.linked_move_operation_ids and op.linked_move_operation_ids[0].move_id.product_uos.id) or op.product_id.uos_id.id
            uom_qty = remaining_qty
            uos_qty = t_uom._compute_qty(uom_id, uom_qty, uos_id)
            uos_vals = {
                'product_uos': uos_id,
                'product_uos_qty': uos_qty,
            }
            res.update(uos_vals)
        """
        Si no tenemos el partner_id la obtenemos del picking relacionado.
        """
        if not res.get('partner_id', False) and op.picking_id.partner_id:
            res.update({'partner_id': op.picking_id.partner_id.id})
            
        return res

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
        res = super(StockMove, self).unlink()
        return res

    def _get_taxes(self, cr, uid, move, context=None):
        res = super(StockMove, self)._get_taxes(cr, uid, move, context=context)
        if not res and not (move.procurement_id.sale_line_id or
                            move.origin_returned_move_id.purchase_line_id):
            fiscal_obj = self.pool.get('account.fiscal.position')
            fpos = move.partner_id.property_account_position
            prod = move.product_id
            taxes = False
            inv_type = context.get('inv_type', False)
            if inv_type in ['out_invoice', 'out_refund']:
                taxes = prod.taxes_id
            elif inv_type in ['in_invoice', 'in_refund']:
                taxes = prod.supplier_taxes_id
            if taxes:
                if fpos:
                    for tax in taxes:
                        res += fiscal_obj.map_tax(cr, uid, fpos, tax,
                                                  context=context)
                else:
                    res = [tax.id for tax in taxes]
        return res

    def attribute_price(self, cr, uid, move, context=None):
        """
            Attribute price to move, important in inter-company moves or receipts with only one partner
        """
        # Pasamos el contexto con la compañia del movimiento para que en caso de obtener el precio
        # del campo standard_price del producto, que es dependiente de la compañia, lo haga correctamente 
        if not context:
            context = {}
        c = context.copy()
        company_id = move.company_id.id
        c.update(company_id=company_id, force_company=company_id)

        return super(StockMove, self).attribute_price(cr, uid, move.with_context(c), context=context)


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    qty_available = fields.Float('Quantity On Hand', compute='_get_qty_available')

    @api.multi
    def _get_qty_available(self):
        for lot in self:
            location_ids = [w.view_location_id.id for w in self.env['stock.warehouse'].search([])]
            lot.qty_available = lot.sudo().product_id.with_context(lot_id=lot.id, location=location_ids).qty_available


