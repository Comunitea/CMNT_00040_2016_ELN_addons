# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields

from openerp.exceptions import ValidationError

WAREHOUSE_STATES = [
    ('waiting', 'Waiting assigment'),
    ('assigned', 'Assigned'),
    ('process', 'In process'),
    ('process_working', 'Working in progress'),
    ('waiting_validation', 'Waiting validatiton'),
    ('done', 'Done')]

class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'
    _description = 'Picking wizard'



    @api.one
    def do_detailed_transfer(self):
        for line in self.item_ids:
            if line.destinationloc_id.in_pack and not line.result_package_id:
                line.result_package_id = self.env['stock.quant.package'].create({})


        res = super(StockTransferDetails, self).do_detailed_transfer()
        if self._context.get('no_transfer', True):
            for op in self.picking_id.pack_operation_ids:
                op.picking_order = op.location_id.picking_order
        return res

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    show_in_pda = fields.Boolean("Show in PDA")
    short_name = fields.Char("Short name in PDA")
    need_confirm = fields.Boolean("Need confirm in PDA")

class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def _compute_state2(self):
        for pick in self:
            if not pick.user_id:
                pick.state_2 = 'waiting'
            else:
                if all([x.qty_done == 0.00 for x in pick.pack_operation_ids]):
                    pick.state_2 = 'assigned'
                elif all([x.qty_done > 0.00 for x in pick.pack_operation_ids]):
                    pick.state_2 = 'done'
                elif all([(x.qty_done > 0.00 or x.pda_checked) for x in pick.pack_operation_ids]):
                    pick.state_2 = 'waiting_validation'
                elif any([x.qty_done > 0.00 for x in pick.pack_operation_ids]):
                    pick.state_2 = 'process_working'
                else:
                    pick.state_2 = 'process'

    @api.multi
    def _compute_ops(self):
        for pick in self:
            pick.done_ops = len(pick.pack_operation_ids.filtered(lambda x: x.qty_done > 0))
            pick.pack_operation_count = len(pick.pack_operation_ids)
            pick.remaining_ops = pick.pack_operation_count - pick.done_ops
            pick.ops_str = "Faltan {:02d} de {:02d}".format(pick.remaining_ops, pick.pack_operation_count)
    
    @api.depends('pack_operation_ids')
    @api.multi
    def _get_pack_operation_count(self):
        for pick in self:
            pick.pack_operation_count = len(pick.pack_operation_ids)

    @api.multi
    def _compute_allow_validate(self):
        for pick in self:
            pick.allow_validate = (pick.state=='assigned' and pick.done_ops>0)

    user_id = fields.Many2one('res.users', 'Operator')
    state_2 = fields.Selection(WAREHOUSE_STATES, string ="Warehouse barcode statue", compute="_compute_state2")
    done_ops = fields.Integer('Done ops', compute="_compute_ops", multi=True)
    remaining_ops = fields.Integer('Remining ops', compute="_compute_ops", multi=True)
    ops_str = fields.Char('Str ops', compute="_compute_ops", multi=True)
    allow_validate = fields.Boolean("Permitir validar", compute="_compute_allow_validate")
    pack_operation_count = fields.Integer('Total ops', compute="_compute_ops", store=True)

    
    
    @api.multi
    def do_transfer(self):
        if self._context.get('no_transfer', True):
            super(StockPicking, self).do_transfer()

    @api.multi
    def confirm_pda_done(self, transfer=False):
        for pick in self.filtered(lambda x:x.state2 in ('process', 'assigned')):
            pick.state2 = 'done'

        if transfer:
            self.filtered(lambda x:x.state == 'assigned').do_transfer()
        return True

    def confirm_from_pda(self, id, transfer=False):
        pick = self.browse[id]
        return pick.confirm_pda_done(transfer)

    @api.model
    def doTransfer(self, vals):
        id = vals.get('id', False)
        pick = self.browse([id])
        pick.pack_operation_ids.filtered(lambda x:not x.pda_done or x.qty_done == 0).unlink()

        if any(op.pda_done for op in pick.pack_operation_ids):
            #reviso si es necesario poner en pack
            pick.pack_operation_ids.put_in_pack()
            for op in pick.pack_operation_ids:
                op.product_qty = op.qty_done
            pick.do_transfer()
            return True
        return False

    @api.model
    def change_pick_value(self, vals):
        print  "------------------- Cambiar valores en las albaranes ----------------\n%s"%vals
        field = vals.get('field', False)
        value = vals.get('value', False)
        id = vals.get('id', False)
        pick = self.browse([id])
        if field == 'user_id' and (not pick.user_id or pick.user_id.id == self._uid):
            pick.write({'user_id': value})
        else:
            return False
        return True

    @api.model
    def _prepare_pack_ops(self, picking, quants, forced_qties):

        if not self.picking_type_id.show_in_pda:
            return super(StockPicking, self)._prepare_pack_ops(picking, quants,
                                                          forced_qties)

        vals = super(StockPicking, self)._prepare_pack_ops(picking, quants, forced_qties)

        location_order = {}

        for val in vals:
            id = val['location_id']
            if id in location_order.keys():
                val['picking_order'] = location_order[id]
            else:
                location_order[id] = self.env['stock.location'].search_read([('id', '=', id)], ['picking_order'])
                val['picking_order'] = location_order[id]

        return vals
       

    @api.multi
    def action_cancel(self):
        super(StockPicking, self).action_cancel()
        if self.wave_id:
            self.write({'wave_id': False})
        return True 
        
    
    @api.model
    def change_pick_value(self, vals):
        
        print  "------------------- Cambiar valores en las albaranes ----------------\n%s"%vals
        field = vals.get('field', False)
        value = vals.get('value', False)
        id = vals.get('id', False)
        pick = self.browse(id)

        if field == 'user_id' and not pick.user_id and not pick.wave_id:
            pick.write({'user_id': value})
        else:
            return False
        return True

    @api.one
    def doAssign(self, vals):
        picking = self.env['stock.picking'].browse(vals.get('id', False))

        if picking:
            picking.write({'user_id': vals.get('user_id', False)})


    @api.multi
    def set_picking_order(self):
        return
