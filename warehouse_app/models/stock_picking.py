# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields, _

from openerp.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    show_in_pda = fields.Boolean("Show in PDA", help="If checked, this picking type will be shown in pda")
    short_name = fields.Char("Short name in PDA", help="Short name to show in PDA")
    need_confirm = fields.Boolean("Need confirm in PDA", help="If checked, this force to process with button after all requeriments done")
    process_from_tree = fields.Boolean("Process from pda tree ops", help="If checked, allow to process op with default values from pick tree ops in pda")


class StockPicking(models.Model):
    _inherit = "stock.picking"

    done_ops = fields.Integer('Done ops', compute="_compute_ops", multi=True, compute_sudo=True)
    pack_operation_count = fields.Integer('Total ops', compute="_compute_ops", copy=False, compute_sudo=True)
    remaining_ops = fields.Integer('Remining ops', compute="_compute_ops", compute_sudo=True, multi=True)
    ops_str = fields.Char('Str ops', compute="_compute_ops", compute_sudo=True, multi=True)

    @api.multi
    def _compute_ops(self):
        for pick in self:
            pick.done_ops = len(pick.pack_operation_ids.filtered(lambda x: x.qty_done > 0))
            pick.pack_operation_count = len(pick.pack_operation_ids)
            pick.remaining_ops = pick.pack_operation_count - pick.done_ops
            pick.ops_str = "{:02d} / {:02d}".format(pick.remaining_ops, pick.pack_operation_count)

    def get_op_picking_order(self, op_vals):
        product_id = op_vals.get('product_id', False)
        if product_id:
            loc_row = self.env['product.product'].browse(product_id).loc_row
        else:
            loc_row = 0
        picking_order = u"{:05d}{:05d}{:05d}".format(int(loc_row), int(op_vals.get('product_id', 0)), int(op_vals.get('lot_id', 0)))
        return picking_order

    @api.model
    def _prepare_pack_ops(self, picking, quants, forced_qties):
        op_data = super(StockPicking, self)._prepare_pack_ops(
            picking, quants, forced_qties)
        for op in op_data:
            op['picking_order'] = picking.get_op_picking_order(op)
        return op_data

    @api.multi
    def _compute_allow_validate(self):
        for pick in self:
            pick.allow_validate = (pick.state == 'assigned' and pick.done_ops > 0)

    user_id = fields.Many2one('res.users', 'Operator')
    allow_validate = fields.Boolean("Permitir validar", compute="_compute_allow_validate")
    show_in_pda = fields.Boolean(related='picking_type_id.show_in_pda')
    locked_in_pda = fields.Boolean('Loked in PDA')

    @api.multi
    def write(self, vals):
        if any(x.locked_in_pda for x in self) and not self._context('from_pda'):
            raise ValidationError (_('This picking (%s) is pda locked'))
        return super(StockPicking, self).write(vals)

    @api.multi
    def set_picking_order(self):
        return

    @api.model
    def pda_do_transfer_from_pda(self, vals):
        id = vals.get('id', False)
        user_id = self.get_pda_ic(id)
        pick = self.sudo(user_id).browse(id)
        body = u"<b>Transferido %s desde PDA</b><ul><li>El día %s</li><li>Usuario: %s</li>" % (pick.name, pick.date_done, pick.env.user.name)
        pick.message_post(body=body)
        if pick.sudo().state in ('cancel', 'done'):
            return False
        return pick.pda_do_transfer()

    @api.multi
    def pda_do_transfer(self):
        self.ensure_one()
        if self.sudo().state in ('cancel', 'done'):
            return False
        if self.company_id != self.env.user.company_id:
            body = u"<b>Transferido desde PDA</b><ul><li>El día %s</li><li>Usuario: %s</li>" % (self.date_done, self.env.user.name)
            self.message_post(body=body)
            ctx = self._context.copy()
            ctx.update(force_user=True)
            user_id = self.get_pda_ic()
            self = self.sudo(user_id).with_context(ctx)
        #No puedo do transfer si pda done está vacío
        if all(not op.pda_done for op in self.pack_operation_ids):
            return False
            raise ValidationError(_("None operation done from pda"))
        self.pack_operation_ids.filtered(lambda x: not x.pda_done or x.qty_done == 0).unlink()
        # Escribo procesado y cantidad en la operación
        for op in self.pack_operation_ids:
            op.write({'product_qty': op.qty_done,
                      'processed': 'true'})

        print "-------------------------------- Transfiriendo %s"%self.name
        self.do_transfer()
        print "-------------------------------- Transferido %s" % self.name
        return True

    @api.model
    def pda_do_assign(self, action):
        if action:
            user_id = self.env.user.id
            if self.state not in ('cancel', 'done'):
                message = "Autoasignado por %s" % self.env.user.name
                self.message_post(message)
                self.write({'user_id': user_id})
        else:
            self.write({'user_id': False})
            
        return True

    @api.model
    def pda_do_assign_from_pda(self, vals):
        id = vals.get('id', False)
        action = vals.get('action', False)
        pick_id = self.browse(id)
        if pick_id.state in ('cancel', 'done'):
            return False
        return pick_id.pda_do_assign(action)

    @api.model
    def pda_do_prepare_partial_from_pda(self, vals):
        id = vals.get('id', False)
        user_id = self.get_pda_ic(id)
        message = "Do prepare partial por %s" % self.env.user.name
        pick = self.sudo(user_id).browse(id)
        if pick.state in ('cancel', 'done'):
            return False
        pick.message_post(message)
        pick.pda_do_prepare_partial()
        return True

    @api.multi
    def pda_do_prepare_partial(self):
        self.ensure_one()
        pick = self
        if pick.sudo().company_id != pick.env.user.company_id:
            user_id = pick.get_pda_ic()
            message = "Do prepare partial por %s" % pick.env.user.name
            pick= pick.sudo(user_id)
            pick.message_post(message)
        if pick.state in ('confirmed', 'partially_available'):
            pick.action_assign()  # Ver si queremos comprobar disponibilidad desde aqui o solo desde ERP
        return pick.do_prepare_partial()

    @api.multi
    def pda_action_assign(self):
        self.ensure_one()
        pick = self
        if pick.sudo().company_id != pick.env.user.company_id:
            user_id = pick.get_pda_ic()
            message = "Action assign por %s" % pick.env.user.name
            pick = pick.sudo(user_id)
            pick.message_post(message)
        res = pick.action_assign()
        if pick.state in ('assigned'):
            pick.do_prepare_partial()
        return res

    @api.multi
    def pda_force_assign(self):
        self.ensure_one()
        pick = self
        if pick.sudo().company_id != pick.env.user.company_id:
            user_id = pick.get_pda_ic()
            message = "Force assign por %s" % pick.env.user.name
            pick = pick.sudo(user_id)
            pick.message_post(message)
        return pick.force_assign()


        self.ensure_one()
        if self.sudo().state in ('cancel', 'done'):
            return False
        if self.company_id == self.env.user.company_id:
            return self.force_assign()
        ctx = self._context.copy()
        ctx.update(force_user=True)
        message = "Force assign por %s" % self.env.user.name
        self.message_post(message)
        return self.with_context(ctx).force_assign()

    @api.model
    def pda_force_assign_from_pda(self, vals):
        id = vals.get('id', False)
        action = vals.get('action', False)
        pick_id = self.browse(id)
        if pick_id.state in ('cancel', 'done'):
            return False
        return pick_id.pda_force_assign(action)

    @api.multi
    def pda_action_cancel(self):
        self.ensure_one()
        if self.sudo().state in ('cancel', 'done'):
            return False
        pick = self
        if pick.sudo().company_id != pick.env.user.company_id:
            user_id = pick.get_pda_ic()
            message = "Cancelado por %s" % pick.env.user.name
            pick = pick.sudo(user_id)
            pick.message_post(message)
        return pick.action_cancel()

    @api.multi
    def pda_do_unreserve(self):
        self.ensure_one()
        if self.sudo().state in ('cancel', 'done'):
            return False
        if self.company_id == self.env.user.company_id:
            return self.do_unreserve()
        ctx = self._context.copy()
        ctx.update(force_user=True)
        message = "Action do unreserve por %s" % self.env.user.name
        self.message_post(message)
        return self.with_context(ctx).do_unreserve()

    @api.multi
    def locked_from_pda(self, action=False):
        for pick in self:
            if pick.sudo().state in ('cancel', 'done'):
                return False
        self.write({'locked_in_pda': action})

    @api.multi
    def get_pda_ic(self, id=False):
        if not id:
            self.ensure_one()
            id = self.id
        sql = u"select intercompany_user_id from res_company rc where id = (select company_id from stock_picking where id = %s)"%id
        self._cr.execute(sql)
        record = self._cr.fetchall()
        return record and record[0][0] or self.env.user.id
