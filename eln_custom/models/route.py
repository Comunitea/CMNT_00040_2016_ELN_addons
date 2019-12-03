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
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class Route(models.Model):
    _name = 'route'
    _description = 'Route Model'

    code = fields.Char('Code', size=32)
    name = fields.Char('Name', size=255)
    carrier_id = fields.Many2one('res.partner', 'Carrier')
    delivery_delay = fields.Float('Delivery Lead Time', required=True,
        help="The average delay in days between the picking transfer and the delivery of the products to customer.")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_ship_create(self):
        res = super(SaleOrder, self).action_ship_create()
        for order in self:
            route_id = order.partner_shipping_id.route_id or \
                order.partner_shipping_id.commercial_partner_id.route_id or \
                False
            if route_id:
                route_id = route_id.id
            order.picking_ids.write({'route_id': route_id})
        return res
    
    
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        for pick in self:
            if pick.date_done and pick.state == 'done':
                effective_date = datetime.strptime(pick.date_done, DEFAULT_SERVER_DATETIME_FORMAT)
                if pick.picking_type_id.code != 'incoming':
                    effective_date += timedelta(days=(pick.route_id and pick.route_id.delivery_delay or 0.0))
                if pick.requested_date:
                    requested_date = datetime.strptime(pick.requested_date, DEFAULT_SERVER_DATE_FORMAT)
                    effective_date = requested_date
                pick.effective_date = effective_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return res
