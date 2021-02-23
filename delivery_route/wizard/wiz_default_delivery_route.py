# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class WizDefaultDeliveryRoute(models.TransientModel):
    _name = 'wiz.default.delivery.route'

    @api.multi
    def set_default_route(self):
        self.ensure_one()
        picking_ids = self._context.get('active_ids', False)
        pickings = self.env['stock.picking'].browse(picking_ids)
        pickings = pickings.filtered(
            lambda r: (
                r.state in ('partially_available', 'assigned', 'confirmed') and
                r.picking_type_code == 'outgoing'
            )
        )
        pickings.action_set_default_route()
        return {'type': 'ir.actions.act_window_close'}
