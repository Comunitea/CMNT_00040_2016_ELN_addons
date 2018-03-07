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

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    show_in_pda = fields.Boolean("Show in PDA")
    short_name = fields.Char("Short name in PDA")

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
            pick.all_ops = len(pick.pack_operation_ids)
            pick.remaining_ops = pick.all_ops - pick.done_ops
            pick.ops_str = "Faltan {:02d} de {:02d}".format(pick.remaining_ops, pick.all_ops)

    @api.multi
    def _compute_allow_validate(self):
        for pick in self:
            pick.allow_validate = (pick.state=='assigned' and pick.done_ops>0)

    user_id = fields.Many2one('res.users', 'Operator')
    state_2 = fields.Selection(WAREHOUSE_STATES, string ="Warehouse barcode statue", compute="_compute_state2")
    done_ops = fields.Integer('Done ops', compute="_compute_ops", multi=True)
    all_ops = fields.Integer('Total ops', compute="_compute_ops", multi=True)
    remaining_ops = fields.Integer('Remining ops', compute="_compute_ops", multi=True)
    ops_str = fields.Char('Str ops', compute="_compute_ops", multi=True)
    partner_id_name = fields.Char(related='partner_id.display_name')
    location_id_name = fields.Char(related="location_id.name")
    location_dest_id_name = fields.Char(related="location_dest_id.name")
    picking_type_id_name = fields.Char(related="picking_type_id.short_name")
    allow_validate = fields.Boolean("Permitir validar", compute="_compute_allow_validate")

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
        pick.pack_operation_ids.filtered(lambda x:not x.pda_done).unlink()

        if any(op.pda_done for op in pick.pack_operation_ids):
            pick.pack_operation_ids.put_in_pack()
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