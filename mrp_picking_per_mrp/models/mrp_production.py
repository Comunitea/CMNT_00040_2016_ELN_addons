# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields

from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare, float_round


class MrpROuting(models.Model):
    _inherit = 'mrp.routing'

    picking_type_id = fields.Many2one('stock.picking.type')

class MrpProduction(models.Model):
    _inherit ='mrp.production'

    hoard_ids = fields.Many2many('stock.picking', string='hoard',
                                 compute='_get_hoard_picking')
    hoard_len = fields.Integer('hoard len', compute='_get_hoard_len')

    @api.one
    @api.depends('move_lines.move_orig_ids', 'move_lines2.move_orig_ids')
    def _get_hoard_len(self):
        pickings = self.env['stock.picking']
        pickings += self.mapped('move_lines.move_orig_ids.picking_id').sorted() \
            | self.mapped('move_lines2.move_orig_ids.picking_id').sorted()
        self.hoard_len = len(pickings)

    @api.one
    @api.depends('move_lines.move_orig_ids', 'move_lines2.move_orig_ids')
    def _get_hoard_picking(self):
        pickings = self.env['stock.picking']
        pickings += self.mapped('move_lines.move_orig_ids.picking_id').sorted() \
            | self.mapped('move_lines2.move_orig_ids.picking_id').sorted()
        self.hoard_ids = pickings or False

    @api.multi
    def get_hoard(self):
        action = self.env.ref('stock.action_picking_tree')
        if not action:
            return
        action = action.read()[0]
        if len(self.hoard_ids) > 1:
            action['domain'] = "[('id','in',[" + ','.join(map(str, self.hoard_ids.ids)) + "])]"
        else:
            res = self.env.ref('stock.view_picking_form')
            action['views'] = [(res.id, 'form')]
            action['res_id'] = self.hoard_ids.id
        action['context'] = False
        return action

    @api.model
    def _create_previous_move(self, move_id, product, source_location_id, dest_location_id):
        proc_obj = self.env['procurement.group']
        move_id = super(MrpProduction, self)._create_previous_move(move_id, product, source_location_id, dest_location_id)
        move = self.env['stock.move'].browse(move_id)
        production_id = move.move_dest_id.raw_material_production_id
        move_dict = {}
        if production_id:
            procurement = proc_obj.search([('name', '=', production_id.name)])
            if not procurement:
                procurement = proc_obj.create({'name': production_id.name})
            else:
                procurement = procurement[0]
            move_dict['group_id'] = procurement.id
            move_dict['picking_type_id'] = production_id.routing_id.picking_type_id.id
        print move_dict
        move.write(move_dict)
        return move.id



