# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields,_

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta

from openerp.exceptions import ValidationError

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    wave_route_link = fields.Boolean("Need wave route link", help="If checked, create new wave when is asigned to any transport route")

class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def write(self, vals):
        if not self._context.get('no_update_routes', False) and vals.get('route_id'):
            for pick in self.filtered(lambda x: x.picking_type_id.wave_route_link and x.state not in ('cancel', 'done')):
                requested_date = vals.get('requested_date', pick.requested_date)
                domain = [('route_id', '=', vals['route_id']), ('state', '=', 'ready')]
                if requested_date:
                    domain += [('requested_date', '=', requested_date)]
                wave_id = self.env['stock.picking.wave'].search(domain, limit=1, order="requested_date desc")
                if not wave_id:
                    values = self.env['stock.picking.wave'].get_wave_route_vals(vals['route_id'], requested_date or fields.Date.today())
                    wave_id = self.env['stock.picking.wave'].create(values)
                vals.update(wave_id=wave_id.id)
                pick.wave_id = wave_id.id
                domain = [('group_id', '=', pick.sudo().group_id.id)]
                picks = self.sudo().env['stock.picking'].search(domain)
                ctx = self._context.copy()
                ctx.update(no_update_routes=True)
                picks.with_context(ctx).write({'wave_id': wave_id.id, 'route_id': vals['route_id']})
        return super(StockPicking, self).write(vals)

