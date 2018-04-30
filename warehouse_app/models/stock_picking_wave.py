# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _

from openerp.exceptions import ValidationError


class StockPickingWave(models.Model):
    _inherit = "stock.picking.wave"


    @api.model
    def _compute_ops(self):
        self.pack_operation_ids = self.picking_ids.mapped('pack_operation_ids')
        

    @api.one
    @api.depends('picking_ids', 'picking_ids.pack_operation_ids')
    def _compute_fields(self):
        if self.picking_ids:
            #self.picking_type_id = self.picking_ids[0].picking_type_id if all(
            #    x.picking_type_id == self.picking_ids[0].picking_type_id for x in
            #    self.picking_ids) else False
            #self.pack_operation_exist = True if len(self.pack_operation_ids)>0 else False
            #self.pack_operation_ids = self.picking_ids.mapped('pack_operation_ids')
            self.pack_operation_count = sum(x.pack_operation_count for x in self.picking_ids)
            self.remaining_ops = sum(x.remaining_ops for x in self.picking_ids)
            self.min_date = min(x.min_date for x in self.picking_ids)
            self.pack_operation_exists = self.pack_operation_count and True
            #self.location_id = self.picking_ids[0].location_id if all(
            #    x.location_id == self.picking_ids[0].location_id for x in
            #    self.picking_ids) else self.picking_type_id.default_location_src_id
            #self.location_dest_id = self.picking_ids[0].location_dest_id if all(
            #    x.location_dest_id == self.picking_ids[0].location_dest_id for x in
            #    self.picking_ids) else self.picking_type_id.default_location_dest_id
            #import ipdb; ipdb.set_trace()
            #self.priority = self.mapped('picking_ids').mapped('move_lines') and max(
            #    self.mapped('picking_ids').mapped('move_lines').mapped('priority')) or '1'


    @api.multi
    def send_wave_to_pda(self):
        for wave in self: 
            if wave.picking_ids == []:
                raise ValidationError (_("Not picks are in this picking wave"))
            wave.picking_ids.write({'user_id': wave.user_id.id})
            wave.state = 'in_progress'
            wave.picking_ids.set_picking_order()


    pack_operation_ids = fields.One2many(
        'stock.pack.operation', string='Related Packing Operations', compute="_compute_ops")
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking type')
    min_date = fields.Datetime('Scheduled Date',
                               help="Scheduled time for the first scheduled date in asociated picking",
                               compute="_compute_fields", store=True)
    location_id = fields.Many2one('stock.location', "Source Location Zone")
    location_dest_id = fields.Many2one('stock.location', "Dest Location Zone")
    pack_operation_count = fields.Integer('Total ops', compute="_compute_fields", store=True)
    remaining_ops = fields.Integer('Remaining ops', compute="_compute_fields", store=True)
    pack_operation_exist = fields.Boolean("Have pack operation", compute="_compute_fields", store=True)

    #priority = fields.Selection(procurement.PROCUREMENT_PRIORITIES,
    #                            string='Priority', compute='_compute_priority',
    #                            store=True, index=True,
    #                            help="Priority for this picking. Setting manually a value here would set it as priority for all the moves")
    #state = fields.Selection(selection_add=[('assigned', 'PDA Ready')])
    
    wave_id = fields.Many2one(
        'stock.picking.wave', string='Picking Wave',
        states={'done': [('readonly', True)]},
        help='Picking wave associated to this picking')
    pack_operation_exist = fields.Boolean(
        'Has Pack Operations', compute='_compute_fields',
        help='Check the existence of pack operation on the picking')

    @api.onchange('picking_type_id')
    def onchange_picking_type_id(self):
        self.location_id = self.picking_type_id.default_location_src_id
        self.location_dest_id = self.picking_type_id.default_location_dest_id
