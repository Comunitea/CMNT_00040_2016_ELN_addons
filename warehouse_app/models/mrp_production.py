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

    in_picking_id = fields.Many2one('stock.picking', 'Raw picking in')
    out_picking_id = fields.Many2one('stock.picking', 'Raw picking out')
    picking_id = fields.Many2one('stock.picking', 'Picking')

    @api.model
    def action_create_picking(self):

        if not self.in_picking_id and self.state in ('draft', 'confirmed'):
            if not self.in_picking_id:
                self.create_pickings('in')
            self.move_lines.write({'picking_id': self.in_picking_id.id})

        if self.move_lines2 and self.state not in ('draft', 'confirmed', 'ready'):
            if not self.out_picking_id:
                self.create_pickings('return')
            for move in self.move_lines2:
                move.copy({'picking_id': self.out_picking_id.id,
                           })

            self.move_lines2.write({'picking_id': self.out_picking_id.id
                                    })


        if self.move_created_ids2:
            if not self.picking_id:
                self.create_pickings('terminated')
            self.move_created_ids2.write({'picking_id':self.picking_id.id})

        for move in moves:
            move.copy({'picking_id': self.out_picking_id.id})


        if not self.picking_id:
            vals = self.get_picking_vals()
            self.picking_id = self.env['stock.picking'].create(vals)

        return
    def create_pickings(self, type):
        if type=='in':
            vals = self.get_in_picking_vals()
            self.in_picking_id = self.env['stock.picking'].create(vals)

        elif type=='return':
            vals = self.get_in_picking_vals()
            self.in_picking_id = self.env['stock.picking'].create(vals)
        elif type=="terminated":
            vals = self.get_picking_vals()
            self.picking_id = self.env['stock.picking'].create(vals)

    def get_out_picking_vals(self):
        location_id = self.routing_id.location_id or self.routing_id.picking_type_id.default_location_dest_id
        vals = {'picking_type_id': self.routing_id.picking_type_id and self.routing_id.picking_type_id.id,
                'location_id': location_id,
                'location_dest_id': self.location_dest_id.id,
                'origin': self.name,
                'company_id': self.company_id.id}
        return vals

    def get_in_picking_vals(self):
        location_id = self.routing_id.location_id or self.routing_id.picking_type_id.default_location_dest_id
        vals = {'picking_type_id': self.routing_id.picking_type_id and self.routing_id.picking_type_id.return_picking_type_id.id,
                'location_id': location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'origin': self.name,
                'company_id': self.company_id.id}
        return vals
