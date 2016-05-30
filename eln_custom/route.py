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
from openerp.osv import orm, fields
from openerp import models, api, exceptions, _


class route(orm.Model):
    _name = 'route'
    _description = 'Route Model'
    _columns = {
        'code': fields.char('Code', size=32),
        'name': fields.char('Name', size=255),
        'carrier_id': fields.many2one('res.partner', 'Carrier'),
        'delivery_delay': fields.float('Delivery Lead Time', required=True, help="The average delay in days between the order transfer and the delivery of the products to customer."),
    }

class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.multi
    def action_ship_create(self):
        res = super(SaleOrder, self).action_ship_create()
        for order in self:
            route_id = order.partner_shipping_id.route_id or order.partner_shipping_id.commercial_partner_id.route_id or False
            if route_id:
                route_id = route_id.id
            order.picking_ids.write({'route_id': route_id})
        return res

