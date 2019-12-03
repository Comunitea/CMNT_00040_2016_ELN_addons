# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos All Rights Reserved
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
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def _read_group_route_ids(self, domain, read_group_order=None, access_rights_uid=None):
        route_obj = self.env['route']
        access_rights_uid = access_rights_uid or self._uid
        order = route_obj._order
        if read_group_order == 'route_id desc':
            order = "%s desc" % order
        route_ids = route_obj._search([],
            order=order, access_rights_uid=access_rights_uid)
        route_ids = route_obj.sudo(access_rights_uid).browse(route_ids)
        result = route_ids.name_get()
        # restore order of the search
        result.sort(lambda x, y: cmp(route_ids.ids.index(x[0]), route_ids.ids.index(y[0])))
        fold = {x[0]:1 for x in result}
        # Se pliega la columna indefinido
        fold[False] = 1
        return result, fold

    _group_by_full = {
        'route_id': _read_group_route_ids
    }

    color_stock = fields.Integer('Color stock',
        compute='_get_color_stock', readonly=True,
        default=-1)
    packages = fields.Float('Packages',
        digits=dp.get_precision('Product UoS'),
        compute='_get_total_values', store=True)
    packages_uos = fields.Float('Packages UoS',
        digits=dp.get_precision('Product UoS'),
        compute='_get_total_values', store=True)
    weight = fields.Float('Weigth',
        digits=dp.get_precision('Stock Weight'),
        compute='_get_total_values', store=True)
    weight_net = fields.Float('Weigth Net',
        digits=dp.get_precision('Stock Weight'),
        compute='_get_total_values', store=True)
    volume = fields.Float('Volume',
        digits=dp.get_precision('Product UoS'),
        compute='_get_total_values', store=True)
    route_id = fields.Many2one(
        'route', 'Route')
    container_numbers = fields.Char('Container numbers',
        related='purchase_id.container_numbers', readonly=True,
        help="Container numbers assigned to the order.")

    @api.multi
    def _get_color_stock(self):
        for pick in self:
            color = -1                 # blanco (cero da error al cargar la vista kanban)
            if pick.state == 'draft':
                color = 3              # amarillo
            elif pick.state == 'cancel':
                color = 1              # gris
            elif pick.state == 'waiting':
                color = 2              # rojo claro 
            elif pick.state == 'confirmed':
                color = 9              # rosa fuerte
            elif pick.state == 'assigned':
                color = 5              # verde oscuro
            elif pick.state == 'partially_available':
                color = 4              # verde claro
            elif pick.state == 'done':
                color = 8              # violeta
            pick.color_stock = color

    @api.multi
    @api.depends('move_lines', 'move_lines.product_id', 'move_lines.product_qty')
    def _get_total_values(self):
        for picking in self:
            packages = packages_uos = weight = weight_net = volume = 0.0
            for line in picking.move_lines:
                packages += line.product_qty
                packages_uos += line.product_qty * (line.product_id.uos_coeff or 1.0)
                if line.product_id:
                    weight += line.product_id.weight * line.product_qty
                    weight_net += line.product_id.weight_net * line.product_qty
                    volume += line.product_id.volume * line.product_qty
            picking.packages = packages
            picking.packages_uos = packages_uos
            picking.weight = weight
            picking.weight_net = weight_net
            picking.volume = volume

    @api.onchange('route_id')
    def onchange_route_id(self):
        self.carrier_id = self.route_id.carrier_id


class StockLocation(models.Model):
    _inherit = 'stock.location'

    name = fields.Char(translate=False)

    @api.model
    def recompute(self):
        # Seguramente no haga falta sobreescribir este método. 
        # Se mantiene de momento
        self._parent_store_compute()
