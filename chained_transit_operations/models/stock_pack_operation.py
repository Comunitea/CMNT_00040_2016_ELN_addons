# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, models, fields, _
import openerp.addons.decimal_precision as dp

from openerp.exceptions import ValidationError


class StockPackOperation (models.Model):

    _inherit = 'stock.pack.operation'


    @api.model
    def _get_picking_orig_id(self):
        moves = self.linked_move_operation_ids.mapped('move_id').mapped('move_orig_id').mapped('picking_id')
        self.picking_orig_id = moves and moves[0] or False

    picking_orig_id = fields.Many2one('stock.picking', compute="_get_picking_orig_id")
    final_location_dest_id = fields.Many2one('stock.location', default=False)