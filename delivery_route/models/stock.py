# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.rrule import rrule
import openerp.addons.decimal_precision as dp


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def _read_group_delivery_route_ids(self, domain, read_group_order=None, access_rights_uid=None):
        delivery_route_obj = self.env['delivery.route']
        access_rights_uid = access_rights_uid or self._uid
        order = delivery_route_obj._order
        if read_group_order == 'delivery_route_id desc':
            order = "%s desc" % order
        delivery_route_ids = delivery_route_obj._search([],
            order=order, access_rights_uid=access_rights_uid)
        delivery_route_ids = delivery_route_obj.sudo(access_rights_uid).browse(delivery_route_ids)
        result = delivery_route_ids.name_get()
        # restore order of the search
        result.sort(lambda x, y: cmp(delivery_route_ids.ids.index(x[0]), delivery_route_ids.ids.index(y[0])))
        fold = {}
        result2 = []
        for x in result:
            domain2 = [('delivery_route_id', '=', x[0])] + domain
            count = self._search(domain2,
                count=True, access_rights_uid=access_rights_uid)
            delivery_route_id = delivery_route_obj.browse(x[0])
            if delivery_route_id.show_always:
                fold[x[0]] = False if count else True
                result2 += [x]
            elif count:
                fold[x[0]] = 0
                result2 += [x]
        # Se pliega la columna indefinido
        # fold[False] = 1
        return result2, fold

    _group_by_full = {
        'delivery_route_id': _read_group_delivery_route_ids
    }

    color_stock = fields.Integer('Color stock',
        compute='_get_color_stock', readonly=True,
        default=-1)
    packages = fields.Float('Packages',
        digits=dp.get_precision('Product UoS'),
        compute='_get_total_values', store=True)
    packages_uos = fields.Float('Packages UoS',
        digits=dp.get_precision('Product UoS'),
        compute='_get_total_values', store=True)
    weight = fields.Float('Weigth',
        digits=dp.get_precision('Stock Weight'),
        compute='_get_total_values', store=True)
    weight_net = fields.Float('Weigth Net',
        digits=dp.get_precision('Stock Weight'),
        compute='_get_total_values', store=True)
    volume = fields.Float('Volume',
        digits=dp.get_precision('Product UoS'),
        compute='_get_total_values', store=True)
    delivery_route_id = fields.Many2one(
        'delivery.route', 'Delivery Route')
    loading_date = fields.Date(
        string='Loading Date',
        help="Date on which the delivery order will be loaded.")
    city = fields.Char(
        string='City',
        related='partner_id.city',
        readonly=True)
    kanban_state = fields.Selection([
        ('normal', 'Pending'),
        ('in_progress', 'In progress'),
        ('done', 'Ready to load'),
        ], string='State of readiness',
        default='normal', copy=False)

    @api.multi
    def _get_color_stock(self):
        # 1 -> gris, 2 -> rojo claro, 3 -> amarillo, 
        # 4 -> verde claro, 5 -> verde oscuro, 8 -> violeta
        # -1 ó 0 -> blanco
        for pick in self:
            color = -1
            today = fields.Date.context_today(self)
            if pick.state in ('done', 'draft', 'cancel'):
                color = 3
            elif not pick.loading_date:
                color = 1
            elif pick.loading_date >= today:
                color = 5
            elif pick.loading_date < today:
                initial_date = datetime.strptime(pick.loading_date, "%Y-%m-%d")
                end_date = datetime.strptime(today, "%Y-%m-%d")
                delayed_days = 1 + len(rrule(
                    freq=3, # Daily
                    byweekday=(0, 1, 2, 3, 4),
                    wkst=0,
                    dtstart=initial_date,
                    until=end_date,
                    interval=1)
                    .between(initial_date, end_date, inc=False)
                )
                if delayed_days > 4:
                    color = 8
                else:
                    color = 2
            pick.color_stock = color

    @api.multi
    @api.depends('move_lines', 'move_lines.product_id', 'move_lines.product_qty')
    def _get_total_values(self):
        for picking in self:
            packages = packages_uos = weight = weight_net = volume = 0.0
            for line in picking.move_lines:
                packages += line.product_qty
                packages_uos += line.product_qty * (line.product_id.uos_coeff or 1.0)
                if line.product_id:
                    weight += line.product_id.weight * line.product_qty
                    weight_net += line.product_id.weight_net * line.product_qty
                    volume += line.product_id.volume * line.product_qty
            picking.packages = packages
            picking.packages_uos = packages_uos
            picking.weight = weight
            picking.weight_net = weight_net
            picking.volume = volume

    @api.onchange('delivery_route_id')
    def onchange_route_id(self):
        self.carrier_id = self.delivery_route_id.carrier_id

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        for pick in self:
            if pick.date_done and pick.state == 'done':
                if pick.picking_type_id.code != 'incoming' and not pick.requested_date:
                    effective_date = datetime.strptime(pick.date_done, DEFAULT_SERVER_DATETIME_FORMAT)
                    effective_date += timedelta(days=(pick.delivery_route_id and pick.delivery_route_id.delivery_delay or 0.0))
                    pick.effective_date = effective_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return res

    @api.model
    def _create_backorder(self, picking, backorder_moves=[]):
        res = super(StockPicking, self)._create_backorder(picking, backorder_moves)
        if res:
            backorder_id = self.env['stock.picking'].browse(res)
            if backorder_id.picking_type_code == 'outgoing':
                delivery_route_id = backorder_id.partner_id.delivery_route_id or \
                    backorder_id.partner_id.commercial_partner_id.delivery_route_id
                vals = {
                    'delivery_route_id': delivery_route_id.id,
                }
                backorder_id.write(vals)
        return res

    @api.multi
    def action_set_default_route(self):
        for pick in self:
            delivery_route_id = pick.partner_id.delivery_route_id or \
                pick.partner_id.commercial_partner_id.delivery_route_id
            pick.delivery_route_id = delivery_route_id

    @api.multi
    def action_print_all_planned_pickings(self):
        if self and self[0].delivery_route_id.show_always:
            domain = [
                ('delivery_route_id', '=', self[0].delivery_route_id.id),
                ('picking_type_code', '=', 'outgoing'),
                ('state', 'in', ('assigned', 'partially_available', 'confirmed')),
            ]
            picking_ids = self.env['stock.picking'].search(domain)
            if picking_ids:
                return self.env['report'].get_action(picking_ids, 'stock.report_picking')

    @api.multi
    def check_kanban_state(self):
        pickings = self.filtered(
            lambda r: (
                r.picking_type_code == 'outgoing' and
                r.state not in ('cancel', 'done') and
                r.kanban_state in ('in_progress', 'done')
            )
        )
        if pickings:
            raise exceptions.Warning(_("Warning!"),
                _("You cannot cancel a picking in progress or ready to load. Change it to pending first and notify the staff involved in the order picking process."))
        return True

    @api.multi
    def action_cancel(self):
        self.check_kanban_state()
        return super(StockPicking, self).action_cancel()

    @api.multi
    def unlink(self):
        self.check_kanban_state()
        return super(StockPicking, self).unlink()
