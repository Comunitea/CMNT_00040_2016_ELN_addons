# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields

from openerp.exceptions import ValidationError


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    show_in_pda = fields.Boolean("Show in PDA", help="If checked, this picking type will be shown in pda")
    short_name = fields.Char("Short name in PDA", help="Short name to show in PDA")
    need_confirm = fields.Boolean("Need confirm in PDA", help="If checked, this force to process with button after all requeriments done")
    process_from_tree = fields.Boolean("Process from pda tree ops", help="If checked, allow to process op with default values from pick tree ops in pda")





class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def _compute_allow_validate(self):
        for pick in self:
            pick.allow_validate = (pick.state=='assigned' and pick.done_ops>0)

    ##copio la funcion de la version 10


    user_id = fields.Many2one('res.users', 'Operator')
    allow_validate = fields.Boolean("Permitir validar", compute="_compute_allow_validate")
    pda_op_ids = fields.One2many('stock.pack.operation', compute = "get_pda_operation")
    show_in_pda = fields.Boolean(related='picking_type_id.show_in_pda')

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
        return super(StockPicking, self)._prepare_pack_ops(picking, quants,forced_qties)

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
        self.filtered(lambda x: x.wave_id).write({'wave_id': False})
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

    @api.multi
    def get_pda_operation(self):
        for pick in self:
            pick.pda_op_ids = [(6, 0, pick[pick.cross_company_field_ops].ids)]



    @api.model
    def pda_do_transfer(self, vals):
        id = vals.get('id', False)
        ctx = self._context.copy()
        pick_sudo = self.sudo().browse([id])
        company_id = pick_sudo.company_id.id
        ctx.update(force_company=company_id)
        pick = self.with_context(ctx).browse([id])
        if all(not x.pda_done for x in pick.pack_operation_ids):
            pick.do_transfer()
            return True

        pick.pack_operation_ids.filtered(lambda x: not x.pda_done or x.qty_done == 0).unlink()
        if any(op.pda_done for op in pick.pack_operation_ids):

            # reviso si es necesario poner en pack
            pick.pack_operation_ids.put_in_pack()
            for op in pick.pack_operation_ids:
                op.write({'product_qty': op.qty_done,
                         'processed': 'true'})

            pick.do_transfer()
            return True
        return False

    @api.model
    def pda_do_assign(self, vals):
        id = vals.get('id', False)
        action = vals.get('action', False)
        if action:
            user_id = self.env.user.id
        else:
            user_id = False

        return self.browse([id]).write({'user_id': user_id})


    @api.model
    def pda_do_prepare_partial(self, vals):
        id = vals.get('id', False)
        ctx = self._context.copy()
        pick_sudo = self.sudo().browse([id])
        company_id = pick_sudo.company_id.id
        ctx.update(force_company=company_id)
        pick = self.with_context(ctx).browse([id])
        pick.action_assign()
        if pick.state in ('assigned', 'partially_available'):
            pick.do_prepare_partial()
        return True