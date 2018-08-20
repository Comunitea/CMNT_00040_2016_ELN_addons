# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta

class StockPickingWave(models.Model):
    _inherit = "stock.picking.wave"

    route_id = fields.Many2one('route')
    requested_date = fields.Date(
        string = 'Requested Date',
        readonly=1,
        default = fields.Date.today(),
        help = "Date by which the customer has requested the items to be delivered. All pick in this wave must have same requested date")


    @api.model
    def create(self, vals):
        if self._context.get('from_route', False):
            route = self.env['route'].browse(self._context.get('from_route'))
            if route:
                vals = self.get_wave_route_vals(route)
        res = super(StockPickingWave, self).create(vals)

        return res


    def get_wave_route_vals(self, route, date=fields.Date.today(), internal=False):
        route_id =self.env['route'].browse(route)
        min_date = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT) - timedelta(days=(route_id and route_id.delivery_delay or 0.0))

        if route_id.ir_sequence_id:
            name = route_id.ir_sequence_id.next_by_id(route_id.ir_sequence_id.id)
        else:
            seq = self.env['ir.sequence'].search([('code', '=', 'picking.wave')], limit=1)
            name = seq.next_by_id(seq.id)

        picking_type_id = route_id.picking_type_id and route_id.picking_type_id.id or False

        vals = {'route_id': route_id.id,
                'name': name,
                'picking_type_id': picking_type_id,
                'state': 'ready',
                'requested_date': date or fields.Date.today(),
                'min_date': min_date.strftime(DEFAULT_SERVER_DATE_FORMAT)}
        return vals

