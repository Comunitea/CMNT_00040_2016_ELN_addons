# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class StockPickingUnreserveMulti(models.TransientModel):
    _name = 'stock.picking.unreserve.multi'

    @api.multi
    def unreserve(self):
        self.ensure_one()
        picking_ids = self._context.get('active_ids', False)
        pickings = self.env['stock.picking'].browse(picking_ids)
        pickings = pickings.filtered(
            lambda r: r.state in ['partially_available', 'assigned', 'confirmed'])
        pickings.do_unreserve()
        return {'type': 'ir.actions.act_window_close'}
