# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields, _
from openerp.addons import decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare, float_round


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.model
    def get_last_move_dest_id(self):
        domain = [('procurement_id', '=', self.id), ('location_dest_id', '=', self.location_id.id), ('state', 'not in', ('done', 'cancel'))]
        moves = self.env['stock.move'].search(domain)
        if moves:
            move = moves and moves[0]
            if move.move_dest_id and move.move_dest_id.move_dest_id:
                return move.move_dest_id.move_dest_id
        return False

    @api.model
    def set_proc_last_move_dest_id(self):

        last_proc_move = self.sudo().get_last_move_dest_id()
        if last_proc_move:
            last = self.move_ids and self.move_ids[0]
            if last:
                vals = {
                    'proc_orig_id': self.id,
                    'move_orig_id': last.id,
                    'move_orig_id_str': u'%s, [%s], %s, %s' % (last.picking_id.name, last.id, last.picking_id.name, last.name),
                    'picking_orig_id': last.picking_id.id
                }
                last_proc_move.write(vals)

    @api.model
    def _run(self, procurement):
        res = super(ProcurementOrder, self)._run(procurement=procurement)
        if procurement.location_id.usage == 'transit':
            procurement.set_proc_last_move_dest_id()
        return res
