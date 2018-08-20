# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields, _

from openerp.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"


    ##TODO PARA HACER UNA VISTA COMO LA DE TIPO DE ALBARANES NO SE HACE DE MOMENTO

    @api.multi
    def _get_picking_wave_count(self):
        result = {}
        for type in self:
            sql = "select count(id) from stock_picking_wave where min_date < '%s' and state='in_progress' and picking_type_id = %s"%(fields.Datetime.now(), type.id)

            self._cr.execute(sql)
            records =self._cr.fetchall()
            count_wave_late = records and records[0][0] or 0
            sql = "select " \
                  "(select count(id) from stock_picking where state ='draft' and wave_id in (select id from stock_picking_wave where state ='in_progress' and picking_type_id = spw.picking_type_id)) as count_draft, " \
                  "(select count(id) from stock_picking where state in ('confirmed', 'waiting') and wave_id in (select id from stock_picking_wave where state = 'in_progress' and picking_type_id = spw.picking_type_id)) as count_not_ready, " \
                  "(select count(id) from stock_picking where state in ('assigned', 'partially_available') and wave_id in (select id from stock_picking_wave where state = 'in_progress'  and picking_type_id = spw.picking_type_id)) as count_ready, " \
                  "(select count(id) from stock_picking where state ='done' and wave_id in (select id from stock_picking_wave where state = 'in_progress' and picking_type_id = spw.picking_type_id)) as count_done, " \
                  "(select count(id) from stock_pack_operation where (picking_id in (select id from stock_picking where state not in ('cancel', 'draft') and wave_id in (select id from stock_picking_wave where state = 'in_progress'  and picking_type_id = spw.picking_type_id)) and pda_done=true)) as pda_done, " \
                  "(select count(id) from stock_pack_operation where (picking_id in (select id from stock_picking where state not in ('cancel', 'draft') and wave_id in (select id from stock_picking_wave where state = 'in_progress' and picking_type_id = spw.picking_type_id)) and pda_done=false)) as pda_not_done, " \
                  "spw.picking_type_id from stock_picking_wave spw " \
                  "join stock_picking sp on sp.wave_id = spw.id where spw.picking_type_id = %s" \
                  "group by spw.picking_type_id"%type.id

            self._cr.execute(sql)
            records = self._cr.fetchall()
            record = records and records[0]
            if records:

                vals = {'count_picking_wave_draft': int(record[0]),
                            'count_picking_wave': int(record[1] + record[2]),
                            'count_picking_wave_waiting': int(record[1]),
                            'count_picking_wave_ready': int(record[2]),
                            'count_picking_wave_done': int(record[3]),
                            'count_pda_done': int(record[4]),
                            'count_pda_not_done': int(record[5]),
                            'count_ops': record[4] + record[5],
                            'count_wave_late': count_wave_late,
                            'rate_count_pda_done': record[4] * 100/(record[4] + record[5]),
                            'rate_picking_wave_late': count_wave_late * 100/(record[1] + record[2])
                            }
                type.count_picking_wave_waiting = int(record[1])
                type.count_picking_wave_ready = int(record[2])

        return

    count_picking_wave_draft = fields.Integer(compute="_get_picking_wave_count", multi=True, help ="Agrupaciones en borrador")
    count_picking_wave_done = fields.Integer(compute="_get_picking_wave_count", multi=True, help="Agrupaciones realizadas")
    count_picking_wave_ready = fields.Integer(compute="_get_picking_wave_count", multi=True, help ="Agrupaciones con todos los albaranes reservados o con algo de disponibilidad")
    count_picking_wave = fields.Integer(compute="_get_picking_wave_count", multi=True)
    count_picking_wave_waiting = fields.Integer(compute="_get_picking_wave_count", multi=True, help ="Agrupaciones con albaranes en espera de otra operación o sin disponibilidad")
    count_wave_late = fields.Integer(compute="_get_picking_wave_count", multi=True)
    count_pda_done = fields.Integer(compute="_get_picking_wave_count", multi=True)
    count_pda_not_done = fields.Integer(compute="_get_picking_wave_count", multi=True)
    count_ops = fields.Integer(compute="_get_picking_wave_count", multi=True)
    rate_count_pda_done = fields.Integer(compute="_get_picking_wave_count", multi=True)
    rate_picking_wave_late = fields.Integer(compute="_get_picking_wave_count", multi=True)

    ## HASTA AQUI

    show_in_pda = fields.Boolean("Show in PDA", help="If checked, this picking type will be shown in pda")
    short_name = fields.Char("Short name in PDA", help="Short name to show in PDA")
    need_confirm = fields.Boolean("Need confirm in PDA", help="If checked, this force to process with button after all requeriments done")
    process_from_tree = fields.Boolean("Process from pda tree ops", help="If checked, allow to process op with default values from pick tree ops in pda")













class StockPicking(models.Model):
    _inherit = "stock.picking"


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

        op_data = super(StockPicking, self)._prepare_pack_ops(picking, quants,
                                                          forced_qties)
        for op in op_data:
            op['picking_order'] = picking.get_op_picking_order(op)
        print op_data
        return op_data

    @api.multi
    def _compute_allow_validate(self):
        for pick in self:
            pick.allow_validate = (pick.state == 'assigned' and pick.done_ops > 0)

    user_id = fields.Many2one('res.users', 'Operator')
    allow_validate = fields.Boolean("Permitir validar", compute="_compute_allow_validate")
    show_in_pda = fields.Boolean(related='picking_type_id.show_in_pda')
    locked_in_pda = fields.Boolean('Loked in PDA')
    is_wave = fields.Boolean(default=False)

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
        print body
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
            print "None operation done from pda"
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
        else:
            user_id = False
        pick = self.get_pda_pick(self.id, "Autoasignado por %s")
        if pick.state not in ('done', 'cancel'):
            return pick.write({'user_id': user_id})

    @api.model
    def pda_do_prepare_partial_from_pda(self, vals):
        id = vals.get('id', False)
        user_id = self.get_pda_ic(id)
        message = "Do prepare partial por %s" % self.env.user.name
        pick = self.sudo(user_id).browse(id)
        if pick.state in ('cancel', 'done'):
            return False
        pick.message_post(message)
        return pick.pda_do_prepare_partial()

    @api.multi
    def pda_do_prepare_partial(self):
        self.ensure_one()
        if self.company_id == self.env.user.company_id:
            self.action_assign() # Ver si queremos comprobar disponibilidad desde aqui o solo desde ERP
            self.do_prepare_partial()
            return True
        ctx = self._context.copy()
        ctx.update(force_user=True)
        if self.state in ('assigned', 'partially_available'):
            message = "Do prepare partial por %s" % self.env.user.name
            self.message_post(message)
            self.with_context(ctx).action_assign() # Ver si queremos comprobar disponibilidad desde aqui o solo desde ERP
            self.with_context(ctx).do_prepare_partial()
            # self.mapped('wave_id')._get_picking_ids_status()
        return True

    @api.multi
    def pda_action_assign(self):
        self.ensure_one()
        if self.sudo().state in ('cancel', 'done'):
            return False
        if self.company_id == self.env.user.company_id:
            res = self.action_assign()
            if self.state == 'assigned':
                self.pda_do_prepare_partial()
            return res
        ctx = self._context.copy()
        ctx.update(force_user=True)
        message = "Action assign por %s" % self.env.user.name
        self.message_post(message)
        res = self.with_context(ctx).action_assign()
        if self.state == 'assigned':
            self.with_context(ctx).pda_do_prepare_partial()
        return res

    @api.model
    def pda_do_assign_from_pda(self, vals):
        id = vals.get('id', False)
        action = vals.get('action', False)
        pick_id = self.browse(id)
        if pick_id.state in ('cancel', 'done'):
            return False
        return pick_id.pda_do_assign(action)

    @api.model
    def pda_force_assign_from_pda(self, vals):
        id = vals.get('id', False)
        user_id = self.get_pda_ic(id)
        message = "Force assign por %s" % self.env.user.name
        pick = self.sudo(user_id).browse(id)
        if pick.state in ('cancel', 'done'):
            return False
        pick.message_post(message)
        return pick.pda_force_assign()

    @api.multi
    def pda_force_assign(self):
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

    @api.multi
    def pda_action_cancel(self):
        self.ensure_one()
        if self.sudo().state in ('cancel', 'done'):
            return False

        ctx = self._context.copy()
        ctx.update(force_user=True)
        message = "Action cancel por %s" % self.env.user.name
        self.message_post(message)
        return self.with_context(ctx).action_cancel()

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
    def action_cancel(self):
        super(StockPicking, self).action_cancel()
        self.filtered(lambda x: x.wave_id).write({'wave_id': False})
        return True

