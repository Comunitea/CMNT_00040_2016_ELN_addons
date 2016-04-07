# -*- coding: utf-8 -*-
# © 2016 Comunitea
# $Jesús Ventosinos Mayor <jesus@comunitea.com>$
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, exceptions, _

class StcokPickingAssignMulti(models.TransientModel):

    _name = 'stock.picking.assign.multi'

    @api.multi
    def assign(self):
        self.ensure_one()
        picking_ids = self._context.get('active_ids', False)
        pickings = self.env['stock.picking'].browse(picking_ids)
        pickings = pickings.filtered(
            lambda r: r.state in ['partially_available', 'confirmed'])
        pickings.action_assign()
        return {'type': 'ir.actions.act_window_close'}
