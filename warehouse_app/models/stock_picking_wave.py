# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _

from openerp.exceptions import ValidationError


class StockPickingWave(models.Model):
    _name = "stock.picking.wave"
    _inherit = ["stock.picking.wave","mail.thread"]

    @api.multi
    def _get_wave_picking_ids(self):

        # hago sql me salto permisos de compañia y no da error en la vista ????
        def sort(element_ids):
            return element_ids.sudo().sorted(key=lambda x: x.picking_order)

        for wave in self.filtered(lambda x: isinstance(x.id, int)):

            sql = u"select sp.id from stock_picking sp " \
                  u"join stock_move sm on sm.picking_id = sp.id " \
                  u"join stock_picking_wave spw on spw.id = sp.wave_id "
            where_int = u"where spw.id = %s and sm.move_dest_id isnull "%wave.id
            groupby = u"group by sp.id"
            sql_int = sql + where_int + groupby
            self._cr.execute(sql_int)
            records = self._cr.fetchall()
            out_ids = [record[0] for record in records]


            sql = "select sp2.id, sp2.name from stock_picking sp2 " \
                  "where sp2.wave_id = %s and sp2.id not in " \
                  "(select sp.id from stock_move sm " \
                  "join stock_move sm2 on sm2.id = sm.move_dest_id " \
                  "join stock_picking sp on sp.id = sm2.picking_id " \
                  "join stock_picking_wave spw on spw.id = sp.wave_id " \
                  "where spw.id = %s)"%(wave.id, wave.id)
            self._cr.execute(sql)
            records = self._cr.fetchall()
            int_ids = [record[0] for record in records]

            sql ="select sp.id from stock_picking sp " \
                 "join stock_picking_wave spw on sp.wave_id = spw.id " \
                 "where spw.id = %s"%wave.id
            self._cr.execute(sql)
            records = self._cr.fetchall()
            ids = [record[0] for record in records]

            wave.picking_out_ids = [(6, 0, self.env['stock.picking'].search([('id', 'in', out_ids)]).ids)]
            wave.picking_int_ids = [(6, 0, self.env['stock.picking'].search([('id', 'in', int_ids)]).ids)]

            #las operaciones no tienen company_id, por lo tanto ....
            wave.pack_operation_ids = self.env['stock.pack.operation'].search([('picking_id', 'in', int_ids)], order='picking_order asc')
            wave.pack_operation_out_ids = sort(self.env['stock.pack.operation'].search([('picking_id', 'in', out_ids)]))
            wave.pack_operation_all_ids = sort(self.env['stock.pack.operation'].search([('picking_id', 'in', ids)]))
        print "Llamo a set_state ...."

        print "Llamo a set_state OK"


    @api.multi
    def _compute_ops(self):
        def sort(element_ids):
            return element_ids.sorted(key=lambda x:  (x.product_id.loc_row, x.product_id, x.lot_id))

        for wave in self.sudo():
            wave.pack_operation_ids = sort(wave.picking_int_ids.mapped('pack_operation_ids'))
            wave.pack_operation_out_ids = sort(wave.picking_out_ids.mapped('pack_operation_ids'))
            wave.pack_operation_all_ids = sort(wave.picking_ids.mapped('pack_operation_ids'))

    @api.multi
    def _compute_fields(self):
        for wave in self:
            sql = "select count(id) as pack_operation_count, count(case when pda_done = true then 1 else null end) as done_ops " \
                  "from stock_pack_operation where picking_id in (select id from stock_picking where wave_id = %s)"%wave.id
            self._cr.execute(sql)
            records = self._cr.fetchall()
            if records:
                record = records and records[0]
                wave.pack_operation_count = record[0]
                wave.done_ops = record[1]
                wave.remaining_ops = wave.pack_operation_count - wave.done_ops
                wave.pack_operation_exist = wave.pack_operation_count != 0
                wave.ops_str = "{:02d}/{:02d}".format(wave.remaining_ops, wave.pack_operation_count)


            #op_ids = wave.pack_operation_ids
            #wave.remaining_ops = sum(not x.pda_done for x in op_ids)
            #wave.pack_operation_count = len(op_ids)
            #wave.done_ops = wave.pack_operation_count - wave.remaining_ops
            #wave.pack_operation_exist = wave.pack_operation_count != 0
            #wave.ops_str = "F {:02d} de {:02d}".format(wave.remaining_ops, wave.pack_operation_count)


        return

    @api.multi
    def get_state(self):
        for wave in self:
            if not wave.route_id and wave.picking_ids:
                wave.min_date = min(x.min_date for x in wave.picking_ids)
            wave.pack_operation_exist = wave.pack_operation_count != 0
            states = list(set(x.state != 'cancel' and x.state for x in wave.picking_int_ids))
            if 'draft' in states:
                picking_state = 'draft'
            elif 'waiting' in states:
                picking_state = 'waiting'
            elif all(x in ('confirmed', 'assigned', 'partially_available') for x in states):
                if all(x.pack_operation_exist for x in wave.picking_int_ids):
                    picking_state = 'assigned'
                else:
                    picking_state = 'confirmed'

            elif all(x in ('done', 'cancel') for x in states):
                picking_state = 'done'

            elif 'confirmed' in states:
                picking_state = 'confirmed'
            elif 'partially_available' in states:
                picking_state = 'partially_available'
            elif 'assigned' in states:
                picking_state = 'assigned'
            else:
                picking_state = 'draft'
            wave.picking_state = picking_state

    @api.multi
    def change_process(self, action):
        self.write({'state': action})

    @api.multi
    def send_wave_to_pda(self):
        for wave in self.sudo():
            if wave.picking_ids == []:
                raise ValidationError (_("Not picks are in this picking wave"))
            if wave.user_id:
                wave.sudo().picking_int_ids.write({'user_id': wave.user_id.id})
            wave.state = 'in_progress'
            wave.pda_action_assign()
            wave.pda_do_prepare_partial()

    @api.multi
    def _is_wave_sqls(self):
        for wave in self:
            sql = "select not count(sm.id) = 0 as multicompany " \
                  "from stock_move sm " \
                  "join stock_picking sp on sp.id = sm.picking_id " \
                  "join stock_picking_wave spw on spw.id = sp.wave_id " \
                  "where spw.id = %s" % wave.id
            self._cr.execute(sql)
            records =self._cr.fetchall()
            wave.multicompany = records and records[0] or False

            sql = "select not count(sm.id) = 0  as chained " \
                  "from stock_move sm " \
                  "join stock_picking sp on sp.id = sm.picking_id " \
                  "join stock_picking_wave spw on spw.id = sp.wave_id " \
                  "where spw.id = %s and sm.move_dest_id isnull" %wave.id
            self._cr.execute(sql)
            records = self._cr.fetchall()
            wave.chained = records and records[0] or False



    pack_operation_all_ids = fields.One2many(
        'stock.pack.operation', string='Related Packing Operations (Internal)', compute="_get_wave_picking_ids", multi=True)
    pack_operation_out_ids = fields.One2many(
        'stock.pack.operation', string='Related Packing Operations (Outgoing)', compute="_get_wave_picking_ids", multi=True)
    pack_operation_ids = fields.One2many(
        'stock.pack.operation', string='Related Packing Operations (Outgoing)', compute="_get_wave_picking_ids", multi=True)

    multicompany = fields.Boolean('Is multicompany', compute="_is_wave_sqls",multi=True, help="Checked if is multicompany")
    chained = fields.Boolean('Is chained wave', compute="_is_wave_sqls", multi=True, help = "Checked if cjained moves in pickings")
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking type')

    min_date = fields.Date('Scheduled Date',
                               help="Scheduled time for the first scheduled date in asociated picking")
    location_id = fields.Many2one('stock.location', "Source Location Zone")
    location_dest_id = fields.Many2one('stock.location', "Dest Location Zone")
    pack_operation_count = fields.Integer('Total ops', compute="_compute_fields", compute_sudo=True)
    remaining_ops = fields.Integer('Remaining ops', compute="_compute_fields", compute_sudo=True)
    done_ops = fields.Integer('Done ops', compute="_compute_fields", multi=True, compute_sudo=True)
    ops_str = fields.Char('Str ops', compute="_compute_fields", compute_sudo=True, multi=True)
    pack_operation_exist = fields.Boolean("Have pack operation", compute="_compute_fields", compute_sudo=True)
    show_in_pda = fields.Boolean(related="picking_type_id.show_in_pda")
    wave_id = fields.Many2one(
        'stock.picking.wave', string='Picking Wave',
        states={'done': [('readonly', True)]},
        help='Picking wave associated to this picking')
    picking_out_ids = fields.One2many('stock.picking', compute="_get_wave_picking_ids", multi=True)
    picking_int_ids = fields.One2many('stock.picking', compute="_get_wave_picking_ids", multi=True)
    group_pack_operation_ids = fields.One2many('stock.pack.operation.group', 'wave_id')
    color = fields.Integer(related='picking_type_id.color')
    state = fields.Selection([('draft', 'Draft'), ('ready', 'Ready'), ('in_progress', 'Running'), ('done', 'Done'), ('cancel', 'Cancelled')], string="State", required=True, copy=False)
    hide_done = fields.Boolean('Show pending works')
    picking_state = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting'), ('confirmed', 'Reserved'), ('assigned', 'Ready'), ('done', 'Done')], string="Picking status",
                                     compute="get_state", compute_sudo=True)
    locked_in_pda = fields.Boolean('Locked in PDA')
    is_wave = fields.Boolean(default=True)

    @api.multi
    def process_stop(self):
        #TODO check si podemos deterne la oleada
        ops = self.pack_operation_all_ids.filtered(lambda x: x.pda_done)
        if ops and False:
            raise ValidationError (_('This wave has operations done in pda'))
        self.change_process('ready')

    @api.multi
    def process_start(self):
        #TODO Check si podemos iniciarlo
        # p.e. Todos los albaranes internos deben de estar reservados

        ops = self.pack_operation_all_ids.filtered(lambda x: x.pda_done)
        if ops and False:
            raise ValidationError(_('This wave has operations done in pda'))
        for wave_id in self:
            wave_id.pda_action_assign_from_pda({'id': wave_id.id})
        self.change_process('in_progress')

    @api.multi
    def confirm_picking(self):
        #primero hago el action confirm de pickin_int
        self.ensure_one()
        self.sudo().write({'state': 'ready'})
        ctx = self._context.copy()
        ctx.update(force_sudo=True)
        return self.sudo().picking_int_ids.with_context(ctx).action_assign()

    @api.multi
    def picking_int_ids_done(self):
        ctx = self._context.copy()
        ctx.update(force_user=True)
        for wave in self.sudo():
            for pick in wave.picking_int_ids:
                body = u"<b>Albarán %s transferido <b><ul><li>El día %s</li><li>Usuario: %s</li>" % (
                pick.name, fields.Datetime.now(), self.env.user.name)
                if pick.state not in ('assigned', 'partially_available'):
                    raise ValidationError(_('Some pickings are still waiting for goods. Please check or force their availability before transfer them.'))
                pick._compute_ops()
                if not pick.pack_operation_exist:
                    raise ValidationError(_('Some pickings are asigned, but without operations, please do prepare partial.'))
                wave.message_post(body)
                pick.pda_do_transfer_from_pda({'id': pick.id})

            # Preparamos los albaranes de salida asociados
            for pick in wave.picking_out_ids:
                if pick.state in ('cancel', 'done'):
                    continue
                pick.with_context(ctx).pda_action_assign()
                #pick.with_context(ctx).do_prepare_partial()
        return

    @api.multi
    def done(self):
        ctx = self._context.copy()
        ctx.update(force_user=True)
        for wave in self:
            for picking in wave.picking_out_ids:
                if picking.state in ('cancel', 'done'):
                    continue
                if picking.backorder_id and not picking.pack_operation_exist:
                    continue
                if not picking.pack_operation_exist:
                    raise ValidationError('Some pickings are asigned, but without operations, please do prepare partial.')
                if picking.state not in ('assigned', 'confirmed', 'partially_available'):
                    raise ValidationError('Some pickings are still waiting for goods. Please check or force their availability before setting this wave to done.')

                picking.with_context(ctx).action_done()
        return self.write({'state': 'done'})


    @api.onchange('picking_ids')
    def get_min_date(self):
        for wave in self:
            if not wave.route_id and wave.picking_ids:
                wave.min_date = min(x.min_date for x in wave.picking_ids)


    @api.onchange('picking_type_id')
    def onchange_picking_type_id(self):
        self.location_id = self.picking_type_id.default_location_src_id
        self.location_dest_id = self.picking_type_id.default_location_dest_id


    @api.multi
    def pda_do_prepare_partial(self):
        ctx = self._context.copy()
        ctx.update(force_user=True)
        message = "Do prepare partial por %s" % self.env.user.name
        for pick in self.sudo().mapped('picking_int_ids'):
            ic_user_id = pick.get_pda_ic()
            pick.sudo(ic_user_id).message_post(message)
            pick.sudo(ic_user_id).do_prepare_partial()
        return True

    @api.multi
    def pda_action_assign(self):
        ctx = self._context.copy()
        ctx.update(force_user=True)
        message = "Action assign por %s" % self.env.user.name
        for pick in self.sudo().mapped('picking_int_ids').filtered(lambda x:x.state not in ('cancel','done')):
            ic_user_id = pick.get_pda_ic()
            pick.sudo(ic_user_id).message_post(message)
            pick.sudo(ic_user_id).action_assign()
        return True

    @api.model
    def pda_do_assign(self, action):
        if action:
            user_id = self.env.user.id
        else:
            user_id = False
        body = u"<h3>%s desde PDA</h3><ul><li>El día %s</li><li>Usuario: %s</li>" % (
            "Asignado" and user_id or "Liberado",
            fields.Datetime.now(),
            self.env.user.name)
        self.do_assign(user_id, body)
        for pick in self.sudo().mapped('picking_int_ids'):
            ic_user_id = pick.get_pda_ic()
            pick.sudo(ic_user_id).message_post(body)
            pick.sudo(ic_user_id).write({'user_id': user_id})
        return True

    @api.model
    def pda_do_transfer(self):
        ctx = self._context.copy()
        ctx.update(force_user=True)
        message = "Do transfer por %s" % self.env.user.name
        for pick in self.sudo().mapped('picking_int_ids'):
            ic_user_id = pick.get_pda_ic()
            pick.sudo(ic_user_id).message_post(message)
            pick.sudo(ic_user_id).pda_do_transfer()
        return True

    @api.multi
    def do_assign(self, user_id=False, body=''):

        for wave_id in self:
            wave_id.message_post(body)
            wave_id.write({'user_id': user_id})


    @api.model
    def pda_do_prepare_partial_from_pda(self, vals):
        id = vals.get('id', False)
        wave_id = self.browse(id)
        return wave_id.pda_do_prepare_partial()

    @api.model
    def pda_do_transfer_from_pda(self, vals):

        id = vals.get('id', False)
        wave_id = self.browse(id)
        message = "Transfiero de %s por %s" % (wave_id.name, self.env.user.name)
        message += "De los picks: %s"%wave_id.picking_int_ids.mapped('name')
        wave_id.message_post(message)
        for pick in wave_id.picking_int_ids:
            vals['id'] = pick.id
            res = pick.pda_do_transfer_from_pda(vals)
        return True

    @api.model
    def pda_action_assign_from_pda(self, vals):
        id = vals.get('id', False)
        wave_id = self.browse(id)
        return wave_id.pda_action_assign()

    @api.model
    def pda_do_assign_from_pda(self, vals):
        id = vals.get('id', False)
        wave_id = self.browse(id)
        action = vals.get('action', False)
        return wave_id.pda_do_assign(action)

    @api.multi
    def locked_from_pda(self, action=False):
        val = {'locked_in_pda': action}
        self.write(val)
        self.picking_ids.write(val)
