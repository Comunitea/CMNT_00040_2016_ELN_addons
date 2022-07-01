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
from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _order = 'id desc'

    address = fields.Char(
        string='Address',
        compute='_get_address',
        search='_search_address')
    sale_id = fields.Many2one(
        string='Sale Order',
        comodel_name='sale.order',
        compute="_get_sale_id")

    @api.multi
    def _get_sale_id(self):
        """
        Esta función está con API antigua en el módulo sale_stock.
        Al hacerla con nueva API mejora sustancialmente el rendimiento en procesos
        tales como creación de facturas de varios albaranes (hasta un 75% más rápido).
        e incluso en la ejecución de planificadores en el caso de crear pickings.
        Esto es debido a una mejor utilización de la caché.
        """
        sale_obj = self.env['sale.order']
        for pick in self:
            domain = [('procurement_group_id', '=', pick.group_id.id)]
            pick.sale_id = pick.group_id and sale_obj.search(domain, limit=1) or False

    @api.multi
    def _get_address(self):
        for pick in self:
            partner = pick.partner_id
            pick.address = (partner.street or '') + \
                (partner.street2 and (' ' + partner.street2) or '')

    @api.model
    def _search_address(self, operator, operand):
        domain = [
            '|',
            ('street', operator, operand),
            ('street2', operator, operand)
        ]
        part = self.env['res.partner'].search(domain)
        return [('partner_id', 'in', part.ids)]

    @api.model
    def _prepare_values_extra_move(self, op, product, remaining_qty):  
        res = super(StockPicking, self)._prepare_values_extra_move(
            op, product, remaining_qty)
        """
        Si no tenemos la UdV la obtenemos del movimiento relacionado o del producto si la tiene
        En caso de no poder obtenerla, no la establecemos (Se podria pasar la UdM como UdV),
        pero no se considera necesario.
        """
        if not res.get('uos_id', False):
            uos_id = op.linked_move_operation_ids and \
                op.linked_move_operation_ids[0].move_id.product_uos.id or \
                op.product_id.uos_id.id
            if uos_id:
                t_uom = self.env['product.uom']
                uom_id = op.product_uom_id.id
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
    _inherit = 'stock.incoterms'

    name = fields.Char(translate=True)


class StockMove(models.Model):
    _inherit = 'stock.move'

    availability = fields.Float(compute='_get_product_availability') # Redefine compute method
    procurement_id = fields.Many2one(select=True) # Redefine index

    @api.multi
    def _get_product_availability(self):
        """
        Igual al original pero con API nueva y omitiendo 'draft' y 'cancel' en el cálculo
        así como cuando la ubicación origen no es interna
        """
        quant_obj = self.env['stock.quant']
        location_obj = self.env['stock.location']
        for move in self:
            if move.state in ('draft', 'cancel') or move.location_id.usage != 'internal':
                availability = 0
            elif move.state == 'done':
                availability = move.product_qty
            else:
                domain = [('id', 'child_of', [move.location_id.id])]
                sublocation_ids = location_obj.search(domain)
                domain = [
                    ('location_id', 'in', sublocation_ids.ids),
                    ('product_id', '=', move.product_id.id),
                    ('reservation_id', '=', False)
                ]
                quant_ids = quant_obj.search(domain)
                availability = sum(quant_ids.mapped('qty'))
                availability = min(move.product_qty, availability)
            move.availability = availability

    @api.multi
    def onchange_quantity(self, product_id, product_qty, product_uom, product_uos):
        """
        Modificamos para que solo permita en unidad de medida la que tiene
        el producto como uom o como uom_po.
        Modificamos para que solo permita en unidad de venta la que tiene el
        producto asignada.
        Con todo esto evitamos sobre todo problemas en precios en facturas
        (_get_price_unit_invoice)
        """
        if product_id:
            product = self.env['product.product'].browse(product_id)
            uos = product.uos_id.id
            uom = product.uom_id.id
            uom_po = product.uom_po_id.id or False
            if product_uom not in (uom, uom_po):
                product_uom = uom
            if product_uos:
                product_uos = uos
        res = super(StockMove, self).onchange_quantity(
            product_id, product_qty, product_uom, product_uos)
        res['value']['product_uom'] = product_uom
        res['value']['product_uos'] = product_uos

        # Cuando se abre una linea existente para editar, si ya habia pasado
        # por aqui va a usar el dominio del articulo anterior.
        # Si es un inconveniente eliminar todo lo que está en el if
        if product_id:
            res['domain'] = {
                'product_uom': [('id', 'in', (uom, uom_po))],
                'product_uos': [('id', 'in', (uos,))]
            }
        else:
            res['domain'] = {
                'product_uom': [],
                'product_uos': []
            }
        return res

    @api.multi
    def unlink(self):
        for move in self:
            if move.state == 'cancel' and move.picking_id.pack_operation_ids:
                move.picking_id.pack_operation_ids.unlink()  # Delete move
        res = super(StockMove, self).unlink()
        return res

    @api.model
    def _get_taxes(self, move):
        res = super(StockMove, self)._get_taxes(move)
        get_taxes = not res and not (
            move.procurement_id.sale_line_id or
            move.origin_returned_move_id.purchase_line_id
        )
        if get_taxes:
            res = []
            fpos = move.picking_id.partner_id.commercial_partner_id.property_account_position
            prod = move.product_id
            taxes = False
            inv_type = self._context.get('inv_type', False)
            if inv_type in ['out_invoice', 'out_refund']:
                taxes = prod.taxes_id
            elif inv_type in ['in_invoice', 'in_refund']:
                taxes = prod.supplier_taxes_id
            if taxes:
                if fpos:
                    for tax in taxes:
                        res += [tax.id for tax in fpos.map_tax(tax)]
                else:
                    res = [tax.id for tax in taxes]
        return res

    @api.model
    def _get_moves_taxes(self, moves, inv_type):
        is_extra_move, extra_move_tax = super(StockMove, self)._get_moves_taxes(moves, inv_type)
        for move in moves:
            get_taxes = (
                is_extra_move[move.id] and 
                not extra_move_tax[move.picking_id, move.product_id]
            )
            if get_taxes:
                fpos = move.picking_id.partner_id.commercial_partner_id.property_account_position
                prod = move.product_id
                taxes = False
                if inv_type in ['out_invoice', 'out_refund']:
                    taxes = prod.taxes_id
                elif inv_type in ['in_invoice', 'in_refund']:
                    taxes = prod.supplier_taxes_id
                if taxes:
                    new_taxes = []
                    if fpos:
                        for tax in taxes:
                            new_taxes += [tax.id for tax in fpos.map_tax(tax)]
                    else:
                        new_taxes = [tax.id for tax in taxes]
                    extra_move_tax[move.picking_id, move.product_id] = [(6, 0, new_taxes)]
        return (is_extra_move, extra_move_tax)

    @api.model
    def attribute_price(self, move):
        # Pasamos el contexto con la compañia del movimiento para que en caso de obtener el precio
        # del campo standard_price del producto, que es dependiente de la compañia, lo haga correctamente 
        move = move.with_context(force_company=move.company_id.id)
        return super(StockMove, self).attribute_price(move)

    @api.multi
    def action_done(self):
        """
            Por defecto el partner_id del movimiento solo se graba cuando el pedido de venta crea el abastecimiento y es ejecutado.
            Para poder filtrar movimientos por el partner_id vamos a hacer que todos los movimientos que pertenezcan a un
            albaran (que tenga establecido el partner_id) escriban ese valor si no tienen ya uno. Se hará al transferir el movimiento.
        """
        res = super(StockMove, self).action_done()
        for move in self:
            if not move.partner_id and move.picking_id.partner_id:
                move.write({'partner_id': move.picking_id.partner_id.id})
        return res

    @api.multi
    def write(self, vals):
        if self.env.context.get('mail_notrack') and vals.get('state') == 'done':
            self = self.with_context(mail_notrack=False)
            # La linea anterior corrige el tracking de cambio de estado (a 'done') al transferir un albarán.
            # Solo lo estaba haciendo bien cuando se generaba un backorder.
        res = super(StockMove, self).write(vals)
        return res


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.multi
    def _mergeable_domain(self):
        """Method from stock quant merge. Adds cost to domain and avoid merge quants with different history_ids"""
        res = super(StockQuant, self)._mergeable_domain()
        res.append(('cost', '=', self.cost))
        where_query = self._where_calc(res)
        from_clause, where_clause, where_clause_params = where_query.get_sql()
        query = """SELECT id FROM stock_quant WHERE %s""" % (where_clause)
        self._cr.execute(query, where_clause_params)
        records = self._cr.fetchall()
        quants = [x[0] for x in records]
        same_history_ids = []
        if quants:
            # Fetch the history_ids manually as it will not do a join with the stock moves then (=> a lot faster)
            self._cr.execute("""SELECT move_id FROM stock_quant_move_rel WHERE quant_id = %s""", (self.id,))
            records = self._cr.fetchall()
            main_history_ids = sorted([x[0] for x in records])
            for quant in quants:
                # Fetch the history_ids manually as it will not do a join with the stock moves then (=> a lot faster)
                self._cr.execute("""SELECT move_id FROM stock_quant_move_rel WHERE quant_id = %s""", (quant,))
                records = self._cr.fetchall()
                comp_history_ids = sorted([x[0] for x in records])
                if main_history_ids == comp_history_ids:
                    same_history_ids += [quant]
        res.append(('id', 'in', same_history_ids))
        return res


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    qty_available = fields.Float('Quantity On Hand',
        compute='_get_qty_available')

    @api.multi
    def _get_qty_available(self):
        for lot in self:
            sw_obj = self.env['stock.warehouse']
            location_ids = sw_obj.search([]).mapped('view_location_id').ids
            lot.qty_available = lot.sudo().\
                product_id.with_context(lot_id=lot.id, location=location_ids).\
                qty_available


class StockInventory(models.Model):
    _inherit = 'stock.inventory'
    _order = 'date desc'

    estimated_valuation = fields.Float('Estimated Valuation',
        digits=dp.get_precision('Account'),
        readonly=True)

    @api.multi
    def _get_estimated_valuation(self):
        for inv in self:
            estimated_valuation = 0.0
            for line in inv.line_ids:
                diff = line.theoretical_qty - line.product_qty
                if diff:
                    price_unit = line.product_id.standard_price
                    estimated_valuation -= diff * price_unit
            inv.estimated_valuation = estimated_valuation

    @api.multi
    def write(self, vals):
        res = super(StockInventory, self).write(vals)
        if vals.get('line_ids', False) or vals.get('state', False):
            self._get_estimated_valuation()
        return res

    @api.multi
    def reset_real_qty(self):
        res = super(StockInventory, self).reset_real_qty()
        self._get_estimated_valuation()
        return res

    @api.multi
    def action_done(self):
        for inv in self:
            if abs(inv.estimated_valuation) > 1.0:
                if not inv.user_has_groups('eln_stock.group_inventory_manager'):
                    raise exceptions.Warning(
                        _("You are not allowed to validate an inventory with value!"))
        return super(StockInventory, self).action_done()


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'
    
    good_warehouse = fields.Boolean(
        string='Good Warehouse',
        help="Check the good warehouse field if the warehouse is a good warehouse.",
        default=False)


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    @api.multi
    def name_get(self):
        return [
            (pt.id, (pt.warehouse_id and
            (pt.warehouse_id.name + ' - ') or '') + pt.name)
            for pt in self
        ]
