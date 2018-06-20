# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare, float_round


WAREHOUSE_STATES = [
    ('waiting', 'Waiting assigment'),
    ('assigned', 'Assigned'),
    ('process', 'In process'),
    ('process_working', 'Working in progress'),
    ('waiting_validation', 'Waiting validatiton'),
    ('done', 'Done')]

from collections import defaultdict

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

class StockPicking(models.Model):
    _inherit = 'stock.picking'


    @api.multi
    def _compute_ops(self):
        for pick in self.sudo():
            pick.done_ops = len(pick.pack_operation_ids.filtered(lambda x: x.qty_done > 0))
            pick.pack_operation_count = len(pick.pack_operation_ids)
            pick.remaining_ops = pick.pack_operation_count - pick.done_ops
            pick.ops_str = "Faltan {:02d} de {:02d}".format(pick.remaining_ops, pick.pack_operation_count)


    @api.depends('move_type','partner_id','launch_pack_operations', 'move_lines.state', 'move_lines.picking_id',
                 'move_lines.partially_available')
    @api.one
    def _compute_state_2(self):
        ''' State of a picking depends on the state of its related stock.move
         - no moves: draft or assigned (launch_pack_operations)
         - all moves canceled: cancel
         - all moves done (including possible canceled): done
         - All at once picking: least of confirmed / waiting / assigned
         - Partial picking
          - all moves assigned: assigned
          - one of the move is assigned or partially available: partially available
          - otherwise in waiting or confirmed state
        '''

        if not self.move_lines and self.launch_pack_operations:
            self.state = 'assigned'
        elif not self.move_lines:
            self.state = 'draft'
        elif any(move.state == 'draft' for move in self.move_lines):  # TDE FIXME: should be all ?
            self.state = 'draft'
        elif all(move.state == 'cancel' for move in self.move_lines):
            self.state = 'cancel'
        elif all(move.state in ['cancel', 'done'] for move in self.move_lines):
            self.state = 'done'
        else:
            # We sort our moves by importance of state: "confirmed" should be first, then we'll have
            # "waiting" and finally "assigned" at the end.
            moves_todo = self.move_lines \
                .filtered(lambda move: move.state not in ['cancel', 'done']) \
                .sorted(key=lambda move: (move.state == 'assigned' and 2) or (move.state == 'waiting' and 1) or 0)
            if self.move_type == 'one':
                self.state = moves_todo[0].state or 'draft'
            elif moves_todo[0].state != 'assigned' and any(
                            x.partially_available or x.state == 'assigned' for x in moves_todo):
                self.state = 'partially_available'
            else:
                self.state = moves_todo[-1].state or 'draft'
            ## TODO revisar en caso de estado esperando con reserva de stock y esprando por disponibilidad
        
        #if self.cross_company and self.state in ('assigned', 'waiting', 'partially_available'):
        #    self.state = self.sudo().compute_cross_state()

    @api.multi
    def _get_related_pick_ids(self):

        for pick in self:

            pick.pick_dest_ids = pick.mapped('move_lines').mapped('move_dest_id').mapped('picking_id')
            pick_ids = self.env['stock.move'].search([('move_dest_id', 'in', pick.move_lines.ids)]).mapped('picking_id')
            #pick_ids += self.env['stock.move'].search([('move_dest_id', 'in', pick_ids.mapped('move_lines').ids)]).mapped('picking_id')
            pick.pick_orig_ids = [(6, 0, pick_ids.ids)]
            pick.related_picks = "Destino: %s \n Origen: %s"%(pick.pick_dest_ids, pick.pick_dest_ids)
            pick.pick_dest = pick.pick_dest_ids and True or False
            pick.pick_orig = pick.pick_orig_ids and True or False


    launch_pack_operations = fields.Boolean("Launch Pack Operations", copy=False)
    done_ops = fields.Integer('Done ops', compute="_compute_ops", multi=True, compute_sudo=True)
    pack_operation_count = fields.Integer('Total ops', compute="_compute_ops", store=True, copy=False, compute_sudo=True)
    remaining_ops = fields.Integer('Remining ops', compute="_compute_ops", compute_sudo=True, multi=True)
    ops_str = fields.Char('Str ops', compute="_compute_ops", compute_sudo=True, multi=True)
    ic_user_id = fields.Many2one(related="company_id.intercompany_user_id")
    ic_user_id_id = fields.Integer('Intercompany user id', compute="get_pda_ic", compute_sudo=True)
    pick_dest_ids = fields.One2many('stock.picking', compute="_get_related_pick_ids", multi=True, compute_sudo=True)
    pick_orig_ids = fields.One2many('stock.picking', compute="_get_related_pick_ids", multi=True, compute_sudo=True)
    pick_orig = fields.Boolean('Has prev picks', compute="_get_related_pick_ids", multi=True, compute_sudo=True)
    pick_dest = fields.Boolean('Has next picks', compute="_get_related_pick_ids", multi=True, compute_sudo=True)
    related_picks = fields.Char("En texto")

    @api.multi
    def write(self, vals):
        if 'wave_id' in vals:
            for pick in self.sudo().mapped('pick_orig_ids'):
                pick.sudo(pick.get_pda_ic()).write({'wave_id': vals['wave_id']})
        return super(StockPicking, self).write(vals)


    @api.multi
    def do_prepare_partial(self):
        if self._context.get('force_user', False):
            for pick in self.sudo():
                super(StockPicking, pick.sudo(pick.get_pda_ic())).do_prepare_partial()
        else:
            return super(StockPicking, self).do_prepare_partial()


        #super(StockPicking, self).do_prepare_partial()
        #for move in self.mapped('move_lines'):
        #    print move.state

    @api.model
    def apply_lots(self):
        wiz_detail_obj = self.env['stock.transfer_details']
        ctx = self._context.copy()
        ctx.update(no_transfer=True)
        wiz_detail = wiz_detail_obj.with_context(ctx).create({'picking_id': self.id})
        wiz_detail.with_context(ctx).do_detailed_transfer()

    @api.multi
    def do_unreserve(self):
        if self._context.get('force_user', False):
            ctx = self._context.copy()
            ctx.update({'force_user': False})
            for pick in self.sudo():
                res = super(StockPicking, pick.sudo(pick.get_pda_ic())).do_unreserve()
            return res
        else:
            return super(StockPicking, self).do_unreserve()

    @api.multi
    def action_assign(self):
        if self._context.get('force_user', False):
            ctx = self._context.copy()
            ctx.update({'force_user': False})
            for pick in self.sudo():
                res = super(StockPicking, pick.sudo(pick.get_pda_ic())).action_assign()
            return res

        else:
            return super(StockPicking, self).action_assign()


    @api.multi
    def action_cancel(self):
        if self._context.get('force_user', False):
            ctx = self._context.copy()
            ctx.update({'force_user': False})
            for pick in self.sudo():
                res = super(StockPicking, pick.sudo(pick.get_pda_ic())).action_cancel()
            return res
        else:
            return super(StockPicking, self).action_cancel()

    @api.multi
    def do_transfer(self):
        if self._context.get('no_transfer', False):
            return
        if self._context.get('force_user', False):
            ctx = self._context.copy()
            ctx.update({'force_user': False})
            for pick in self.sudo():
                res = super(StockPicking, pick.sudo(pick.get_pda_ic())).do_transfer()
            return res
        else:
            return super(StockPicking, self).do_transfer()

    @api.multi
    def rereserve_pick(self):
        """
        This can be used to provide a button that rereserves taking into account the existing pack operations
        RESCRITA PARA V8 Y APROVECHO PARA SUDO
        """
        for pick in self.sudo():
            new_uid = self.get_pda_ic(pick.id) or self.env.user.id
            move_ids = pick.move_lines.filtered(lambda x: x.state not in ('done', 'cancel'))
            pick.sudo(new_uid).rereserve_quants(pick.sudo(new_uid), move_ids.ids)

    @api.multi
    def run_asociated_procurements(self):
        group_id = self.sudo().group_id
        proc_ids = group_id.procurement_ids.filtered(lambda x:x.state == 'confirmed')
        for proc in proc_ids:
            proc.sudo().run()
        if proc_ids:
            self.run_asociated_procurements()

    ### v10
    @api.multi
    def partial_do_prepare_partial(self):
        self.ensure_one()
        #igual que do prepare partial pero sin borrar ops ya hechas y con ensure one
        ctx = self._context.copy()
        ctx.update(no_recompute=True)
        moves_to_prepare = self._context.get('moves_to_prepare', [])
        if not moves_to_prepare:
            return

        moves = self.env['stock.move'].browse(moves_to_prepare)

        forced_qties = {}
        picking_quants = []
        for move in moves.filtered(lambda x: x.picking_id == self): ##REDUNDANTE PERO POR SI ACASO
            if move.state not in ('assigned', 'confirmed', 'waiting'):
                continue
            move_quants = move.reserved_quant_ids
            picking_quants += move_quants
            forced_qty = (move.state == 'assigned') and move.product_qty - sum([x.qty for x in move_quants]) or 0
            if float_compare(forced_qty, 0, precision_rounding=move.product_id.uom_id.rounding) > 0:
                if forced_qties.get(move.product_id):
                    forced_qties[move.product_id] += forced_qty
                else:
                    forced_qties[move.product_id] = forced_qty
            for vals in self._prepare_pack_ops(self, picking_quants, forced_qties):
                self.env['stock.pack.operation'].create(vals)

        self.do_recompute_remaining_quantities()
        self.write({'recompute_pack_op': False})

    ### ESTAS 2 FUNCIONES SIRVEN PARA RECUPERAR E INSTANCIAR EL PICKING CON EL USUARIO INTERCOMPAÑIA ###
    @api.model
    def get_pda_pick(self, id, action=False):
        pick = self.sudo(self.get_pda_ic(id)).browse([id])
        if action:
            message = action % self.env.user.name
            pick.message_post(message)
        return pick

    @api.multi
    def get_pda_ic(self, id=False):
        if not id:
            self.ensure_one()
            id = self.id
        sql = u"select intercompany_user_id from res_company rc where id = (select company_id from stock_picking where id = %s)"%id
        self._cr.execute(sql)
        record = self._cr.fetchall()
        return record and record[0][0] or self.env.user.id
