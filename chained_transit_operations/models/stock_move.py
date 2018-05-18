# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields, _
from openerp.addons import decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare, float_round


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _get_v10_product_availability(self):

        sublocation_ids = self.env['stock.location'].search([('id', 'child_of', [self.location_id.id])])
        print [x.name for x in sublocation_ids]
        domain = [('location_id', 'in', sublocation_ids.ids), ('product_id', '=', self.product_id.id),('reservation_id', '=', False)]
        if self._context.get('force_company', False):
            domain += [('company_id', '=', self._context.get('force_company'))]
        res = self.env['stock.quant'].read_group(domain, ['product_id', 'qty'], ['product_id'])
        print res
        return res and res[0]['qty'] or 0.00

    # SOBRE ESCRITA A V10
    @api.multi
    def _get_product_availability(self):
        for move in self:
            if move.state == 'done':
                move.availability = move.product_qty
            else:
                move.availability = move._get_v10_product_availability()


    @api.model
    def _get_str_qty_info(self, precision, text='reserved'):
        uom_obj = self.env['product.uom']
        total_available = min(self.product_qty, self.reserved_availability + self.availability)
        total_available = uom_obj._compute_qty_obj(self.product_id.uom_id, total_available, self.product_uom,
                                                   round=False)
        total_available = float_round(total_available, precision_digits=precision)
        info = str(total_available)
        # look in the settings if we need to display the UoM name or not
        if self.env.user.has_group('product.group_uom'):
            info += ' ' + self.product_uom.name
        if self.reserved_availability:
            if self.reserved_availability != total_available:
                # some of the available quantity is assigned and some are available but not reserved
                reserved_available = uom_obj._compute_qty_obj(self.product_id.uom_id, self.reserved_availability,
                                                              self.product_uom, round=False)
                reserved_available = float_round(reserved_available, precision_digits=precision)
                info += _(' (%s %s)') % (str(reserved_available), text)
            else:
                # all available quantity is assigned
                info += _(' (%s)')% text
        return info

    #SOBRE ESCRITA A V10
    @api.multi
    def _get_string_qty_information(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for move in self:
            
            if move.state in ('draft', 'done', 'cancel') or move.location_id.usage != 'internal':
                move.string_availability_info = ''  # 'not applicable' or 'n/a' could work too
                continue
            if not move.reserved_availability and move.move_orig_id:
                ic_user_id = move.move_orig_id.sudo().ic_user_id.id
                ctx = move._context.copy()
                ctx.update(force_company= move.move_orig_id.sudo(ic_user_id).company_id.id)
                info = move.move_orig_id.sudo(ic_user_id).with_context(ctx)._get_str_qty_info(precision, 'pre-reserved')
            else:
                info = move._get_str_qty_info(precision)
            move.string_availability_info = info
        return


    proc_orig_id = fields.Many2one('procurement.order', 'First proc in chained moves')
    #move_orig_ids = fields.One2many(related='proc_orig_id.move_ids')
    move_orig_id = fields.Many2one('stock.move', 'First move in chained moves')
    move_orig_id_str = fields.Char('First move in chained moves')
    picking_orig_id = fields.Many2one('stock.picking', 'First move pick in chained moves')
    string_availability_info = fields.Char(string="Availability", help='Show various information on stock availability for this move', compute="_get_string_qty_information")
    prereserved_availability = fields.Float(related = 'move_orig_id.reserved_availability', string='Pre reserved qty', compute_sudo=True)
    state = fields.Selection(selection_add=[('pre-assigned', 'Pre reserved')])
    cross_company = fields.Boolean(related='picking_id.picking_type_id.cross_company')
    availability = fields.Float(string='Quantity Available', readonly=True, compute="_get_product_availability",
                                    help='Quantity in stock that can still be reserved for this move')
    ic_user_id = fields.Many2one(related="company_id.intercompany_user_id")
    def get_prev_moves(self):
        return self.filtered(lambda x:x.procure_method == 'make_to_order'
                               and not x.move_dest_id
                               and x.move_orig_id
                               and x.move_orig_id.state == 'assigned')
    @api.multi
    def action_assign(self):
        return super(StockMove, self).action_assign()

    @api.multi
    def act_prev_chained_moves(self):
        for move in self.get_prev_moves().filtered(lambda x: x.state in ('assigned')):
            lot_id = move.linked_move_operation_ids.mapped('lot_id')
            package_id = move.linked_move_operation_ids.mapped('package_id')
            qty = move.linked_move_operation_ids.mapped('qty_done')
            vals = {'restrict_lot_id' :  lot_id and lot_id[0].id,
                    'restrict_package_id': package_id and package_id[0].id,
                    'product_uom_qty': qty}
            move.move_orig_id.write(vals)


    @api.model
    def create(self, vals):
        res = super(StockMove, self).create(vals)
        return res

    @api.model
    def get_state_from_pre_move(self, state=False):
        print self.sudo().move_orig_id.picking_id.name
        prev_state = state or self.move_orig_id and self.sudo().move_orig_id.state or False
        if prev_state in ('partially_available', 'confirmed'):
            new_state = 'confirmed'
        elif prev_state in ('assigned', 'done'):
            new_state = 'assigned'
        else:
            return
        self.state = new_state
        return prev_state


    @api.multi
    def write(self, vals):
        if self._context.get('force_sudo', False):
            res = super(StockMove, self.sudo()).write(vals)
        else:
            res = super(StockMove, self).write(vals)
        return res