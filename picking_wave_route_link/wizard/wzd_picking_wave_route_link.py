# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta

class WzdPickingWaveRouteLink(models.TransientModel):

    _name = 'wzd.picking.wave.route.link'
    _description = 'Add link to waves and routes'

    requested_date = fields.Date('Requested date', required=1, default = fields.Date.today())
    link_pickings = fields.Boolean("Link picks", help="If checked, find and link picks in route and date")

    @api.multi
    def create_waves(self):
        ids = self._context.get('active_ids', False)
        new_waves = []
        if ids:
            route_ids = self.env['route'].browse(ids)
            wave_ids = self.env['stock.picking.wave']
            for route_id in route_ids:
                domain = [('route_id', '=', route_id.id),('requested_date','=', self.requested_date), ('state', '=', 'in_progress')]
                wave_id = wave_ids.search(domain, limit=1)
                if not wave_id:
                    vals = self.env['stock.picking.wave'].get_wave_route_vals(route_id.id, self.requested_date)
                    wave_id = self.env['stock.picking.wave'].create(vals)
                if self.link_pickings:
                    domain = [('route_id', '=', route_id.id), ('requested_date', '=', self.requested_date)]
                    self.env['stock.picking'].search(domain).write({'wave_id': wave_id.id})
                new_waves.append(wave_id.id)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking.wave',
            'domain': [('id', 'in', new_waves)],
            'view_mode': 'tree, form',
        }
