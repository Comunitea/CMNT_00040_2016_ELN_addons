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

    cross_company = fields.Boolean("Cross company ops", help="If checked, this picking have previous moves/ops and transfer then before transfer itself", default=False)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def _get_cross_company_ops_field(self):
        for pick in self:
            pick.cross_company_field_ops = 'pack_operation_ids' if pick.cross_company else 'cross_pack_operation_ids'

    @api.multi
    def _compute_ops(self):
        for pick in self:
            field = pick.cross_company_field_ops
            pick.done_ops = len(pick[field].filtered(lambda x: x.qty_done > 0))
            pick.pack_operation_count = len(pick[field])
            pick.remaining_ops = pick.pack_operation_count - pick.done_ops
            pick.ops_str = "Faltan {:02d} de {:02d}".format(pick.remaining_ops, pick.pack_operation_count)

    @api.multi
    def _get_picking_orig_ids(self):
        for pick in self.filtered(lambda x: x.cross_company):
            picking_orig_ids = pick.sudo().move_lines.mapped('move_orig_id').mapped('picking_id')
            pick.picking_orig_ids = [(6,0, picking_orig_ids.ids)]

    @api.model
    def compute_cc_state(self):
        cc_state = 'draft'
        field = self.cross_company_field_ops
        if not self.user_id:
            cc_state = 'waiting'
        else:
            if all([x.qty_done == 0.00 for x in self[field]]):
                cc_state = 'assigned'
            elif all([x.qty_done > 0.00 for x in self.pack_operation_ids]):
                cc_state = 'done'
            elif all([(x.qty_done > 0.00 or x.pda_checked) for x in self[field]]):
                cc_state = 'waiting_validation'
            elif any([x.qty_done > 0.00 for x in self[field]]):
                cc_state = 'process_working'
            else:
                cc_state = 'process'
        return cc_state

    @api.depends('move_type', 'launch_pack_operations', 'pack_operation_ids', 'cross_pack_operation_ids')
    @api.model
    def _compute_cc_state(self):
        if self.cross_company:
            self.cc_state = self.sudo().compute_cc_state()
        else:
            self.cc_state = self.compute_cc_state()

    @api.model
    def compute_cross_state(self):
        #hay que llamarla con sudo para ver todas los picks y moves asociados
        orig_ids = self.picking_orig_ids
        if any(pick.state == 'waiting' for pick in orig_ids):
            return 'waiting'
        elif any(pick.state == 'partially_available' for pick in orig_ids):
            return 'partially_available'
        elif all(pick.state == 'confirmed' for pick in orig_ids):
            return self.state
        elif all(pick.state == 'assigned' for pick in orig_ids):
            if any(move.state == 'partially_available' for move in self.move_lines):
                return 'partially_available'
            elif all(move.state == 'assigned' for move in self.move_lines):
                return 'assigned'
        return self.state
        
    @api.depends('move_type','partner_id','launch_pack_operations', 'move_lines.state', 'move_lines.picking_id',
                 'move_lines.partially_available', 'cross_pack_operation_ids')
    @api.one
    def _compute_state(self):
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
        if not self.move_lines and self.launch_pack_operations:#_get_picking_orig_ids
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


    launch_pack_operations = fields.Boolean("Launch Pack Operations", copy=False)
    # procure_method = 'make_to_stock' es el primero
    # procure_method = 'make_to_order' el resto
    cc_state = fields.Selection(WAREHOUSE_STATES, string="Warehouse barcode statue", compute='_compute_cc_state')
    state = fields.Selection([
        ('draft', 'Draft'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'), ('done', 'Done')], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n"
             " * Waiting Availability: still waiting for the availability of products\n"
             " * Partially Available: some products are available and reserved\n"
             " * Ready to Transfer: products reserved, simply waiting for confirmation.\n"
             " * Transferred: has been processed, can't be modified or cancelled anymore\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore")

    picking_orig_ids = fields.One2many('stock.picking', compute="_get_picking_orig_ids", compute_sudo=True)

    cross_company = fields.Boolean(related='picking_type_id.cross_company')
    cross_company_field_ops = fields.Char(compute="_get_cross_company_ops_field")
    cross_pack_operation_ids = fields.One2many('stock.pack.operation', compute="get_operation_sudo", compute_sudo=True)
    done_ops = fields.Integer('Done ops', compute="_compute_ops", multi=True, compute_sudo=True,)
    pack_operation_count = fields.Integer('Total ops', compute="_compute_ops", store=True, copy=False, compute_sudo=True)
    remaining_ops = fields.Integer('Remining ops', compute="_compute_ops", compute_sudo=True,multi=True)
    ops_str = fields.Char('Str ops', compute="_compute_ops", compute_sudo=True, multi=True)
    ic_user_id = fields.Many2one(related="company_id.intercompany_user_id")
    #def do_prepare_partial(self):
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
    def chained_action_assign(self):
        for pick in self:
            picks_to_check = pick.sudo().picking_orig_ids.filtered(lambda x: x.state in ['confirmed', 'partially_available'])
            for picking_orig_id in picks_to_check:
                ctx = self._context.copy()
                ctx.update(force_company=picking_orig_id.company_id.id)
                picking_orig_id.sudo(picking_orig_id.ic_user_id.id).action_assign()
                picking_orig_id.sudo(picking_orig_id.ic_user_id.id).do_prepare_partial()

    @api.multi
    def action_assign(self):
        self.filtered(lambda x: x.cross_company).chained_action_assign()
        return super(StockPicking, self).action_assign()


    @api.multi
    def do_transfer(self):

        if self._context.get('no_transfer', False):
            return
        ctx = self._context.copy()
        for pick in self:
            if pick.cross_company:
                moves_to_reassign = []
                moves_to_unreserve = []
                prev_picks = pick.sudo().picking_orig_ids.filtered(lambda x:x.state in ['assigned', 'partially_available', 'confirmed'])
                if prev_picks:
                    for prev_pick in prev_picks:
                        moves_to_unreserve = pick.move_lines.filtered(lambda x: x.move_orig_id.id in [prev_pick.move_lines.ids])
                        moves_to_unreserve.mapped('linked_move_operation_ids').mapped('operation_id').unlink()
                        moves_to_unreserve.do_unreserve()
                        ctx.update(force_company=prev_pick.company_id.id,
                                    no_transfer=False,
                                    from_cross_company=True)
                        if prev_pick.state in ['confirmed', 'assigned', 'partially_available']:
                            prev_pick.sudo().with_context(ctx).do_transfer()
                        moves_to_reassign += moves_to_unreserve

                    if moves_to_reassign:
                        m2r_str = [u'%s, %s' % (x.name, x.picking_id.name) for x in moves_to_reassign]
                        moves_to_reassign.action_assign()
                        ctx = pick._context.copy()
                        ctx.update(active_model='stock.picking',
                                   no_transfer = True,
                                   from_cross_company=True,
                                   active_ids=[self.id],
                                   active_id=self.id)
                        pick.rereserve_quants(pick, moves_to_reassign.ids)
                        ctx =self._context.copy()
                        ctx.update(moves_to_prepare=moves_to_reassign.ids)
                        pick.partial_do_prepare_partial()

        super(StockPicking, self).do_transfer()

    @api.model
    def get_operation_sudo(self):
        for pick in self:
            if not pick.cross_company:
                pick.cross_pack_operation_ids = [(6, 0, pick.pack_operation_ids.ids)]
            else:
                op_ids = pick.sudo().move_lines.mapped('move_orig_id').mapped('picking_id').mapped('pack_operation_ids')
                cross_pack_operation_ids = pick.move_lines.filtered(
                    lambda x: not x.move_orig_id).mapped('linked_move_operation_ids').mapped('operation_id') + op_ids

                if cross_pack_operation_ids:
                    pick.cross_pack_operation_ids = [(6, 0, cross_pack_operation_ids.ids)]

    def rereserve_quants(self, cr, uid, picking, move_ids=[], context=None):
        if picking.cross_company:
            ctx = context.copy()
            ctx.update(force_company=picking.company_id.id)
            super(StockPicking, self).rereserve_quants(cr, uid, picking, move_ids=move_ids, context=ctx)
        else:
            super(StockPicking, self).rereserve_quants(cr, uid, picking, move_ids=move_ids, context=context)


    def rereserve_pick(self, cr, uid, ids, context=None):
        """
        This can be used to provide a button that rereserves taking into account the existing pack operations
        """
        for pick in self.browse(cr, uid, ids, context=context):
            for prev_pick in pick.sudo().filtered(lambda x:x.cross_company).picking_orig_ids:
                ctx = context.copy()
                ctx.update(force_company=prev_pick.company_id.id)
                prev_pick.with_context(ctx).rereserve_quants(prev_pick, move_ids=[x.id for x in prev_pick.move_lines
                                                               if x.state not in ('done', 'cancel')])
            pick.rereserve_quants(pick, move_ids=[x.id for x in pick.move_lines
                                                             if x.state not in ('done', 'cancel')])

    @api.multi
    def run_asociated_procurements(self):

        group_id = self.sudo().group_id

        proc_ids = group_id.procurement_ids.filtered(lambda x:x.state == 'confirmed')
        for proc in proc_ids:
            proc.sudo().run()
        if proc_ids:
            self.run_asociated_procurements()


    @api.multi
    def partial_do_prepare_partial(self):
        return self.partial_do_prepare_partial()


    ### v10
    @api.multi
    def partial_do_prepare_partial(self):
        #igual que do prepare partial pero sin borrar ops ya hechas
        ctx = self._context.copy()
        ctx.update(no_recompute=True)
        moves_to_prepare = self._context.get('moves_to_prepare', [])
        if not moves_to_prepare:
            self.env['stock.pack.operation'].search([('picking_id', 'in', self.ids)]).unlink()

        if moves_to_prepare:
            moves = self.sudo().env['stock.move'].browse(moves_to_prepare)
        else:
            moves = self.sudo().mapped('move_lines')

        for pick in self:
            user_id = pick.ic_user_id
            ctx.update(force_company=pick.company_id.id)
            picking = pick.sudo(user_id).with_context(ctx)
            forced_qties = {}
            picking_quants = []
            for move in moves.filtered(lambda x: x.picking_id == picking):
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
                for vals in picking._prepare_pack_ops(picking, picking_quants, forced_qties):
                    self.env['stock.pack.operation'].create(vals)

        self.do_recompute_remaining_quantities()
        self.write({'recompute_pack_op': False})

    @api.cr_uid_ids_context
    def do_prepare_partial_v8(self, cr, uid, picking_ids, context=None):
        ## Lo pongo aquí para comparar
        context = context or {}
        pack_operation_obj = self.pool.get('stock.pack.operation')
        # used to avoid recomputing the remaining quantities at each new pack operation created
        ctx = context.copy()
        ctx['no_recompute'] = True

        # get list of existing operations and delete them
        existing_package_ids = pack_operation_obj.search(cr, uid, [('picking_id', 'in', picking_ids)], context=context)
        if existing_package_ids:
            pack_operation_obj.unlink(cr, uid, existing_package_ids, context)
        for picking in self.browse(cr, uid, picking_ids, context=context):
            forced_qties = {}  # Quantity remaining after calculating reserved quants
            picking_quants = []
            # Calculate packages, reserved quants, qtys of this picking's moves
            for move in picking.move_lines:
                if move.state not in ('assigned', 'confirmed', 'waiting'):
                    continue
                move_quants = move.reserved_quant_ids
                picking_quants += move_quants
                forced_qty = (move.state == 'assigned') and move.product_qty - sum([x.qty for x in move_quants]) or 0
                # if we used force_assign() on the move, or if the move is incoming, forced_qty > 0
                if float_compare(forced_qty, 0, precision_rounding=move.product_id.uom_id.rounding) > 0:
                    if forced_qties.get(move.product_id):
                        forced_qties[move.product_id] += forced_qty
                    else:
                        forced_qties[move.product_id] = forced_qty
            for vals in self._prepare_pack_ops(cr, uid, picking, picking_quants, forced_qties, context=context):
                pack_operation_obj.create(cr, uid, vals, context=ctx)
        # recompute the remaining quantities all at once
        self.do_recompute_remaining_quantities(cr, uid, picking_ids, context=context)
        self.write(cr, uid, picking_ids, {'recompute_pack_op': False}, context=context)