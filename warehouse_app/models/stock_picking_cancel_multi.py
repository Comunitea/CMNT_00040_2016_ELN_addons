# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from openerp import models, fields, api, exceptions, _

class StcokPickingCancelMulti(models.TransientModel):

    _name = 'stock.picking.cancel.multi'

    @api.multi
    def cancel(self):
        self.ensure_one()
        picking_ids = self._context.get('active_ids', False)
        pickings = self.env['stock.picking'].browse(picking_ids)
        pickings = pickings.filtered(
            lambda r: r.state in ['partially_available', 'confirmed'])
        pickings.action_cancel()
        return {'type': 'ir.actions.act_window_close'}
