# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, exceptions, _
from openerp import tools
from datetime import datetime
from openerp.addons.product import _common
from openerp.tools import float_is_zero
from openerp.tools.float_utils import float_round
import openerp.addons.decimal_precision as dp


PRODUCTION_STATES = [
    ('draft', 'New'),
    ('confirmed', 'Awaiting Raw Materials'),
    ('ready', 'Ready to Produce'),
    ('in_production', 'Production Started'),
    ('finished', 'Finished'),
    ('validated', 'Validated'),
    ('closed', 'Closed'),
    ('cancel', 'Cancelled'),
    ('done','Done')
]

PRODUCTION_TYPES = [
    ('normal', 'Normal'),
    ('rework', 'Rework'),
    ('sample', 'Sample'),
    ('special', 'Special')
]


class ChangeProductionQty(models.TransientModel):
    _inherit = 'change.production.qty'

    @api.model
    def _update_product_to_produce(self, prod, qty):
        res = super(ChangeProductionQty, self)._update_product_to_produce(prod, qty)
        uom_obj = self.env['product.uom']
        proc_obj = self.env['procurement.order']
        for m in prod.move_created_ids:
            if m.product_uos:
                uos_qty = uom_obj._compute_qty(m.product_uom.id, qty, m.product_uos.id)
                m.write({'product_uos_qty': uos_qty})
        procs = proc_obj.search([('production_id', '=', prod.id)])
        if procs:
            body = _('Manufacturing Order <em>%s</em> has changed the quantity: %s -> %s') % (procs.production_id.name, procs.product_qty, qty)
            procs.message_post(body=body)
            uos_qty = prod.product_uos and uom_obj._compute_qty(prod.product_uom.id, qty, prod.product_uos.id) or 0.0
            procs.write({'product_qty': qty, 'product_uos_qty': uos_qty})
        return res

    @api.multi
    def change_prod_qty(self):
        """
        Cuando se cambia la cantidad debe volver a comprobar las reservas,
        pues si ya estaban hechas era para la cantidad anterior.
        """
        res = super(ChangeProductionQty, self).change_prod_qty()
        record_id = self._context.get('active_id', False)
        assert record_id, _('Active Id not found')
        prod = self.env['mrp.production'].browse(record_id)
        # Solo actuamos sobre los movimientos que ya tenían algo reservado
        move_ids = prod.mapped('move_lines').filtered(
            lambda r: (
                r.state in ('confirmed', 'waiting', 'assigned') and
                len(r.reserved_quant_ids) > 0
            )
        )
        move_ids.do_unreserve()
        move_ids.action_assign()
        return res


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'
    _order = 'sequence'

    operators_ids = fields.Many2many(
        'hr.employee', string='Operators',
        rel='hr_employee_mrp_workcenter_rel',
        id1='workcenter_id', id2='employee_id'
    )
    performance_factor = fields.Float('Performance',
        size=8, required=True, default=1,
        help="Performance factor for this workcenter")
    sequence = fields.Integer('Sequence')


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    alternatives_routing_ids = fields.Many2many(
        'mrp.routing', string='Alternatives routings',
        rel='mrp_bom_routing_rel',
        id1='bom_id', id2='routing_id'
    )

    @api.multi
    def _check_product(self):
        for bom in self:
            if bom.product_id in bom.bom_line_ids.mapped('product_id'):
                return False
        return True

    _constraints = [
        (_check_product, 'BoM line product should not be same as BoM product.', ['product_id']),
    ]

    @api.model
    def _bom_explode(self, bom, product, factor, properties=None, level=0, routing_id=False, previous_products=None, master_bom=None):

        def _factor(factor, product_efficiency, product_rounding):
            factor = factor / (product_efficiency or 1.0)
            factor = _common.ceiling(factor, product_rounding)
            if factor < product_rounding:
                factor = product_rounding
            return factor

        def _get_vals(wc_use, operators, operators_n, factor, bom, wc, routing):
            qty_per_cycle = self.env['product.uom']._compute_qty(
                wc_use.uom_id.id, wc_use.qty_per_cycle, bom.product_uom.id)
            oper = []
            if operators_n and operators:
                for op in range(0, (operators_n)):
                    oper.append(operators[op])
            lang = self.env.user.lang or u'es_ES'
            hour = (factor * bom.product_qty) * (wc_use.hour_nbr or 1.0) / (qty_per_cycle or 1.0)
            hour = hour * (wc.time_efficiency or 1.0)
            hour = hour / (wc.performance_factor or 1.0)
            hour = hour / (routing.availability_ratio or 1.0)
            hour = float(hour)
            return {
                'name': tools.ustr(wc_use.name) + u' - ' + tools.ustr(bom.product_id.with_context(lang=lang).name),
                'routing_id': routing.id,
                'workcenter_id': wc.id,
                'sequence': 0, # level + (wc_use.sequence or 0), # Ponemos siempre 0 porque vamos a usar para ordenar en kanban
                'operators_ids': oper and [(6, 0, oper)] or False,
                'cycle': wc_use.cycle_nbr * (factor * bom.product_qty),
                'time_start': wc_use.time_start,
                'time_stop': wc_use.time_stop,
                'hour': hour,
                'real_time': hour,
                'availability_ratio': routing.availability_ratio or 1.0,
            }

        result, result2 = super(MrpBom, self)._bom_explode(
            bom, product, factor, properties=None, level=0, routing_id=False,previous_products=None, master_bom=None)
        factor = _factor(factor, bom.product_efficiency, bom.product_rounding)
        result2 = []
        routing = self.env['mrp.routing'].browse(routing_id) or bom.routing_id or False
        if routing:
            for wc_use in routing.workcenter_lines:
                wc = wc_use.workcenter_id
                operators = []
                if wc_use.operators_ids:
                    for oper in wc_use.operators_ids:
                        operators.append(oper.id)
                result2.append(_get_vals(wc_use, operators, wc_use.operators_number, factor, bom, wc, routing))
        return result, result2


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    @api.multi
    def _check_product(self):
        for bom_line in self:
            if bom_line.product_id == bom_line.bom_id.product_id:
                return False
        return True

    _constraints = [
        (_check_product, 'BoM line product should not be same as BoM product.', ['product_id']),
    ]


class MmrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    operators_ids = fields.Many2many(
        'hr.employee', string='Operators',
        rel='hr_employee_mrp_routing_workcenter_rel',
        id1='routing_workcenter_id', id2='employee_id'
    )
    capacity_per_cycle = fields.Float('Capacity per Cycle',
        help="Number of operations this Work Center can do in parallel. If this Work Center represents a team of 5 workers, the capacity per cycle is 5.")
    time_start = fields.Float('Time before prod.',
        help="Time in hours for the setup.")
    time_stop = fields.Float('Time after prod.',
        help="Time in hours for the cleaning.")
    qty_per_cycle = fields.Float('Qty x cycle')
    uom_id = fields.Many2one(
        'product.uom', 'UoM')
    operators_number = fields.Integer(u'Operators Nº')

    @api.onchange('workcenter_id')
    def onchange_workcenter_id(self):
        """ Changes Operators if workcenter changes.
        @param workcenter_id: Changed workcenter_id
        @return:  Dictionary of changed values
        """
        self.operators_ids = self.workcenter_id.operators_ids


class ProductionStops(models.Model):
    _name = 'production.stops'

    name = fields.Char('Name', size=32, required=True)
    reason = fields.Char('Reason', size=255, required=True)
    time = fields.Float('Time', required=True)
    in_production = fields.Boolean('In Production', default=True,
        help="Stop registered during production time")
    production_workcenter_line_id = fields.Many2one(
        'mrp.production.workcenter.line', 'Production workcenter line')
    company_id = fields.Many2one(
        'res.company', 'Company',
        related='production_workcenter_line_id.company_id',
        readonly=True, store=True)


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'
    _order = 'id'

    @api.multi
    def _read_group_workcenter_ids(self, domain, read_group_order=None, access_rights_uid=None):
        workcenter_obj = self.env['mrp.workcenter']
        workcenter_line_obj = self.env['mrp.production.workcenter.line']
        access_rights_uid = access_rights_uid or self._uid
        order = workcenter_obj._order
        if read_group_order == 'workcenter_id desc':
            order = '%s desc' % order
        workcenter_ids = workcenter_obj._search([], 
            order=order, access_rights_uid=access_rights_uid)
        workcenter_ids = workcenter_obj.sudo(access_rights_uid).browse(workcenter_ids)
        result = workcenter_ids.name_get()
        # restore order of the search
        result.sort(lambda x, y: cmp(workcenter_ids.ids.index(x[0]), workcenter_ids.ids.index(y[0])))
        fold = {}
        for workcenter in workcenter_ids:
            domain = [
                ('workcenter_id', '=', workcenter.id),
                ('production_state', 'in', ('ready', 'confirmed', 'in_production'))
            ]
            count = workcenter_line_obj._search(domain,
                count=True, access_rights_uid=access_rights_uid)
            fold[workcenter.id] = False if count else True
        return result, fold

    _group_by_full = {
        'workcenter_id': _read_group_workcenter_ids
    }

    operators_ids = fields.Many2many(
        'hr.employee', string='Operators',
        rel='hr_employee_mrp_prod_workc_line_rel',
        id1='workcenter_line_id', id2='employee_id'
    )
    production_stops_ids = fields.One2many(
        'production.stops', 'production_workcenter_line_id', 'Production stops')
    time_start = fields.Float('Time before prod.',
        help="Time in hours for the setup.")
    time_stop = fields.Float('Time after prod.',
        help="Time in hours for the cleaning.")
    gasoleo_start = fields.Float('Gasoleo start')
    gasoleo_stop = fields.Float('Gasoleo stop')
    color = fields.Integer('Color Index')
    move_id = fields.Many2one(
        'stock.move', 'Move',
        related='production_id.move_prod_id', readonly=True)
    color_production = fields.Integer('Color production',
        related='production_id.color_production', readonly=True)
    routing_id = fields.Many2one(
        'mrp.routing', 'Routing',
        related='production_id.routing_id', readonly=True)
    real_time = fields.Float('Real time')
    priority = fields.Selection([
        ('0', 'Not urgent'),
        ('1', 'Normal'),
        ('2', 'Urgent'),
        ('3', 'Very Urgent')], 'Priority',
        related='production_id.priority',
        readonly=True, store=True)
    production_type = fields.Selection(PRODUCTION_TYPES, 'Type of production',
        related='production_id.production_type',
        readonly=True)
    product_uos_qty = fields.Float('Product UoS Quantity',
        related='production_id.product_uos_qty', readonly=True)
    product_uos = fields.Many2one(
        'product.uom', 'Product UoS',
        related='production_id.product_uos', readonly=True)
    kanban_name = fields.Char('Kanban name',
        compute='_get_kanban_name', readonly=True)
    availability_ratio = fields.Float('Availability ratio', size=8, default=1,
        help="Availability ratio expected for this workcenter line. "
        "The estimated time was calculated according to this ratio.")
    workorder_planned_state = fields.Selection([
        ('0', 'No planned'),
        ('1', 'Planned')], 'Planned state')
    production_state = fields.Selection(PRODUCTION_STATES, 'Production Status',
        related='production_id.state',
        readonly=True)
    company_id = fields.Many2one(
        'res.company', 'Company',
        related='production_id.company_id',
        readonly=True, store=True)

    @api.multi
    def _get_kanban_name(self):
        for line in self:
            line.kanban_name = line.production_id.name + u' - ' + ((line.name).split('-')[0])[:-1]

    @api.multi
    def modify_production_order_state(self, action):
        """ Modifies production order state if work order state is changed.
        @param action: Action to perform.
        @return: Nothing
        """
        self.ensure_one()
        prod = self.production_id
        if action == 'start':
            if prod.state =='confirmed':
                prod.force_production()
                prod.signal_workflow('button_produce')
            elif prod.state in ('ready', 'in_production', 'finished', 'validated', 'closed'):
                prod.signal_workflow('button_produce')
            else:
                raise exceptions.Warning(
                    _('Error!'),
                    _('Manufacturing order cannot be started in state "%s"!') % (prod.state))
        else:
            return super(MrpProductionWorkcenterLine, self).modify_production_order_state(action)
        return

    @api.multi
    def open_mrp_production_form(self):
        self.ensure_one()
        prod = self.production_id
        if not prod:
            return False
        return {
            'name': 'MRP Production',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'mrp.production',
            'res_id': prod.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'context': self._context
        }

    @api.multi
    def unlink(self):
        if any(x.state not in ('draft', 'cancel') for x in self):
            raise exceptions.Warning(
                _('Error!'),
                _('You cannot delete a work order which is not in draft or cancelled.'))
        res = super(MrpProductionWorkcenterLine, self).unlink()
        return res


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """ Display only operators of the workcenterlines of the mrp.production route"""
        operator_ids = []
        if self._context.get('routing_id', False):
            rout_obj = self.env['mrp.routing']
            routing_id = rout_obj.browse(self._context['routing_id'])
            for line in routing_id.workcenter_lines:
                if line.operators_ids:
                    for op in line.operators_ids:
                        operator_ids.append(op.id)
            args = (args or []) + [['id', 'in', operator_ids]]
        return super(HrEmployee, self).search(
            args=args, offset=offset, limit=limit, order=order, count=count)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """ Display only operators of the workcenterlines of the mrp.production route"""
        res = super(HrEmployee, self).name_search(
            name, args=args, operator=operator, limit=limit)
        if self._context.get('routing_id', False):
            domain = (args or []) + [('name', operator, name)]
            recs = self.search(domain, limit=limit)
            res = recs.name_get()
        return res


class MrpRouting(models.Model):
    _inherit = 'mrp.routing'

    availability_ratio = fields.Float('Availability ratio', size=8, default=1, required=True,
        help="Availability ratio expected for this production route. "
        "The estimated time of workcenter line will be calculated according to this ratio. "
        "Therefore, this will affect the calculation of costs or the time of availability of a production center.")

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """ Overwrite in order to search only routings or alternative
        routings of the material list
        """
        routing_ids = []
        if self._context.get('bom_id', False):
            bom_obj = self.env['mrp.bom']
            bom_id = bom_obj.browse(self._context['bom_id'])
            if bom_id.routing_id:
                routing_ids.append(bom_id.routing_id.id)
            for r in bom_id.alternatives_routing_ids:
                routing_ids.append(r.id)
            args = (args or []) + [['id', 'in', routing_ids]]
        return super(MrpRouting, self).search(
            args=args, offset=offset, limit=limit, order=order, count=count)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """
        Display only routes defined in material list routes or alternative
        routes. Uses the overwrited search
        """
        res = super(MrpRouting, self).name_search(
            name, args=args, operator=operator, limit=limit)
        if self._context.get('bom_id', False):
            domain = (args or []) + [('name', operator, name)]
            recs = self.search(domain, limit=limit)
            res = recs.name_get()
        return res


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    _order = 'name desc'

    date_planned = fields.Datetime(readonly=False) # Redefined
    routing_id = fields.Many2one(ondelete='restrict') # Redefined
    date = fields.Datetime('Creation Date',
        states={'cancel': [('readonly', True)], 'done': [('readonly', True)]},
        default=fields.Datetime.now, copy=False)
    state = fields.Selection(PRODUCTION_STATES) # Redefined
    note = fields.Text('Notes')
    workcenter_lines = fields.One2many(readonly=False) # Redefined
    origin = fields.Char(readonly=False, # Redefined
        states={'cancel': [('readonly', True)], 'done': [('readonly', True)]})
    color_production = fields.Integer('Color production',
        compute='_get_color_production', readonly=True)
    theo_cost = fields.Float('Theorical Cost',
        digits=dp.get_precision('Product Price'), copy=False)
    production_type = fields.Selection(PRODUCTION_TYPES, 'Type of production',
        default='normal', copy=False)

    @api.multi
    def _get_color_production(self):
        for prod in self:
            color_production = -1      # blanco (cero da error al cargar la vista kanban)
            if prod.priority == '0':   # Prioridad no urgente
                color_production = 4   # verde claro
            elif prod.priority == '1': # Prioridad normal
                color_production = 3   # amarillo
            elif prod.priority == '2': # Prioridad urgente
                color_production = 2   # rojo claro
            elif prod.priority == '3': # Prioridad muy urgente
                color_production = 1   # gris
            prod.color_production = color_production

    @api.multi
    def modify_consumption(self):
        ctx = dict(
            self._context,
            active_model=self._name,
            active_ids=self.ids,
            active_id=self.ids[0]
        )
        mod_cons_obj = self.env['mrp.modify.consumption'].with_context(ctx) 
        return mod_cons_obj.create({}).wizard_view()

    @api.model
    def _costs_generate(self, production):
        """ Calculates total costs at the end of the production.
        @param production: Id of production order.
        @return: Calculated amount.
        """
        amount = 0.0
        analytic_line_obj = self.env['account.analytic.line']
        for wc_line in production.workcenter_lines:
            wc = wc_line.workcenter_id
            if wc.costs_journal_id and wc.costs_general_account_id:
                # Cost per hour
                value = wc_line.hour * wc.costs_hour
                account = wc.costs_hour_account_id.id
                if value and account:
                    amount += value
                    analytic_line_obj.sudo().create({
                        'name': wc_line.name + ' (H)',
                        'amount': value,
                        'account_id': account,
                        'general_account_id': wc.costs_general_account_id.id,
                        'journal_id': wc.costs_journal_id.id,
                        'ref': wc.code,
                        'product_id': wc.product_id.id,
                        'unit_amount': wc_line.hour,
                        'product_uom_id': wc.product_id and wc.product_id.uom_id.id or False
                    })
        return amount

    @api.model
    def _make_production_produce_line(self, production):
        move_id = super(MrpProduction, self)._make_production_produce_line(production)
        move = self.env['stock.move'].browse(move_id)
        move_name = _('PROD: %s') % production.name
        move.write({'name': move_name})
        return move_id

    @api.onchange('product_uos_qty')
    def product_uos_qty_change(self):
        if self.product_id.uos_id:
            qty_uom = float(self.product_uos_qty / (self.product_id.uos_coeff or 1.0))
            self.product_qty = qty_uom
            self.product_uos = self.product_id.uos_id
        else:
            self.product_uos_qty = False
            self.product_uos = False

    @api.model
    def action_produce(self, production_id, production_qty, production_mode, wiz=False):
        stock_move_obj = self.env['stock.move']
        uom_obj = self.env['product.uom']
        production = self.browse(production_id)
        production_qty_uom = uom_obj._compute_qty(
            production.product_uom.id, production_qty, production.product_id.uom_id.id)
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        main_production_move = False
        default_mode = self._context.get('default_mode', False)
        if production_mode == 'produce':  # New Case: Produce Only
            produced_products = {}
            for produced_product in production.move_created_ids2:
                if produced_product.scrapped:
                    continue
                if not produced_products.get(produced_product.product_id.id, False):
                    produced_products[produced_product.product_id.id] = 0
                produced_products[produced_product.product_id.id] += produced_product.product_qty
            for produce_product in production.move_created_ids:
                subproduct_factor = self._get_subproduct_factor(production.id, produce_product.id)
                lot_id = wiz and wiz.lot_id.id or False
                qty = min(subproduct_factor * production_qty_uom, produce_product.product_qty) # Needed when producing more than maximum quantity
                new_moves = produce_product.action_consume(
                    qty, location_id=produce_product.location_id.id, restrict_lot_id=lot_id)
                stock_move_obj.browse(new_moves).write({'production_id': production_id})
                remaining_qty = subproduct_factor * production_qty_uom - qty
                if not float_is_zero(remaining_qty, precision_digits=precision):
                    # In case you need to make more than planned
                    # consumed more in wizard than previously planned
                    extra_move_id = produce_product.copy(
                        default={'product_uom_qty': remaining_qty, 'production_id': production_id})
                    extra_move_id.action_confirm()
                    extra_move_id.action_done()
                if produce_product.product_id == production.product_id:
                    main_production_move = produce_product.id
            if default_mode != 'consume' and not production.move_created_ids:
                production.signal_workflow('button_finished_validated')
        else:
            if not main_production_move:
                main_production_move = production.move_created_ids2 and production.move_created_ids2[0].id
            # Añadimos al contexto 'main_production_move'
            # para poder escribirlo en el write y en el action_consume()
            self = self.with_context(main_production_move=main_production_move)
            res = super(MrpProduction, self).action_produce(
                production_id, production_qty, production_mode, wiz=wiz)
            if default_mode != 'consume' and not production.move_created_ids:
                production.signal_workflow('button_finished_validated')
            if default_mode == 'consume':
                # Custom behaivor, set closed state
                production.signal_workflow('button_validated_closed')
        return True

    @api.multi
    def action_finished(self):
        for production in self:
            production.write({'state': 'finished'})
        return True

    @api.multi
    def action_validated(self):
        tmpl_obj = self.env['product.template']
        for production in self:
            theo_cost = tmpl_obj._calc_price(production.bom_id, test=True)
            production.write({'state': 'validated', 'theo_cost': theo_cost})
        return True

    @api.multi
    def action_close(self):
        tmpl_obj = self.env['product.template']
        precision = self.env['decimal.precision'].precision_get('Product Price')
        for production in self:
            date = max(
                [x.date
                for x in production.move_created_ids2
                if x.state == 'done' and not x.scrapped]
                or [None]
            )
            for move in production.move_lines2.filtered(lambda r: r.state == 'done'):
                # Establecemos en los movimiento de consumos los precios de coste de producto que tenía en la fecha
                # que se realizó el producto finalizado, para que coincida con la misma posición
                # en la que se calcula el theo_cost. Esto es debido a que los consumos se pueden hacer más
                # tarde que la validación del producto terminado (action_validated)
                price_unit = tmpl_obj.get_history_price(
                    move.product_id.product_tmpl_id.id, move.company_id.id, date=date)
                # Aplicamos el redondeo que tendría el campo standard_price,
                # ya que get_history_price devuelve el valor sin precision
                price_unit = float_round(price_unit, precision_digits=precision) 
                price_unit = price_unit or move.product_id.standard_price
                move.write({'price_unit': price_unit})
            production.write({'state': 'closed'})
            production.check_produced_lot()
        return True

    @api.multi
    def action_cancel(self):
        """ Cancels the production order and related stock moves.
        @return: True
        """
        res = super(MrpProduction, self).action_cancel()
        # Put related procurements in cancel state
        proc_obj = self.env['procurement.order']
        procs = proc_obj.search([('production_id', 'in', self.ids)])
        procs.write({'state': 'cancel'})
        return res

    @api.multi
    def action_in_production(self):
        """
        Overwrite to set startworking state of all workcenter lines instead
        only one.
        """
        for workcenter_line in self.mapped('workcenter_lines'):
            workcenter_line.signal_workflow('button_start_working')
        return super(MrpProduction, self).action_in_production()

    @api.multi
    def action_production_end(self):
        prod_line_obj = self.env['mrp.production.product.line']
        res = super(MrpProduction, self).action_production_end()
        for production in self:
            bom = production.bom_id
            finished_qty = sum(
                [x.product_uom_qty
                for x in production.move_created_ids2 
                if x.state == 'done' and not x.scrapped]
            )
            factor = self.env['product.uom']._compute_qty(
                production.product_uom.id, finished_qty, bom.product_uom.id)
            new_qty = factor / bom.product_qty
            routing_id = production.routing_id.id
            result, result2 = self.env['mrp.bom']._bom_explode(
                bom, production.product_id, new_qty, routing_id=routing_id)
            prod_lines = result
            production.product_lines.unlink()
            for line in prod_lines:
                line['production_id'] = production.id
                prod_line_obj.create(line)
        # Nos aseguramos de que la trazabilidad hacia arriba de la producción es correcta
        # Hay casos en los que se eliminan las lineas de consumos y se agragan nuevas,
        # momento en el que se pierde la traza
        self.update_production_traceability()
        return res

    @api.multi
    def update_production_traceability(self):
        for production in self:
            for move in production.move_created_ids2.filtered(
                    lambda r: r.state == 'done'):
                if move.production_id:  # Is final production move
                    raw_ids = move.production_id.move_lines
                    raw_ids |= move.production_id.move_lines2.filtered(
                        lambda r: r.state != 'cancel' and not r.scrapped)
                    move.write({'parent_ids': [(6, 0, raw_ids.ids)]})
        return True

    @api.multi
    def unlink(self):
        """ Unlink the production order and related stock moves.
        @return: True
        """
        if any(x.state not in ('draft', 'confirmed', 'ready', 'in_production', 'cancel')
               for x in self):
            raise exceptions.Warning(
                _('Error!'),
                _('You cannot delete a production which is not cancelled.'))
        prods_to_cancel = self.filtered(lambda r: r.state != 'cancel')
        if prods_to_cancel:
            prods_to_cancel.action_cancel()
        moves_to_unlink = self.mapped('move_created_ids2') + self.mapped('move_lines2')
        moves_to_unlink.unlink()
        wc_lines_to_unlink = self.mapped('workcenter_lines')
        wc_lines_to_unlink.unlink()
        res = super(MrpProduction, self).unlink()
        return res

    @api.multi
    def update_production_priority(self):
        domain = [
            ('priority', '!=', '3'),
            ('state', 'in', ['confirmed', 'ready'])
        ]
        production_ids = self or self.search(domain)
        for production in production_ids:
            product_id = production.product_id
            ctx = dict(self._context, location=production.location_dest_id.id)
            product_available = product_id.with_context(ctx)._product_available()[product_id.id]
            qty_to_compare = product_available['qty_available'] - product_available['outgoing_qty']
            company_id = production.company_id
            domain = company_id and [('company_id', '=', company_id.id)] or []
            domain.append(('product_id', '=', product_id.id))
            op = self.env['stock.warehouse.orderpoint'].search(domain, limit=1)
            min_qty = security_qty = 0
            if op:
                min_qty = min(op.product_min_qty, op.product_max_qty)
                security_qty = op.product_security_qty
            if qty_to_compare <= 0:
                priority = '2' # Urgente
            elif qty_to_compare <= security_qty:
                priority = '1' # Normal
            elif qty_to_compare <= min_qty:
                priority = '0' # No urgente
            else:
                priority = '0' # No urgente
            if production.priority != priority:
                production.write({'priority': priority})
        return True

    @api.multi
    def check_produced_lot(self, raw_lots=False, produced_lots=False):
        for production in self:
            check_production_lot_date_type = production.product_id.check_production_lot_date_type
            if check_production_lot_date_type in (False, 'no_check'):
                continue
            if not raw_lots:
                raw_moves = production.move_lines2.filtered(
                   lambda r: r.state == 'done' and not r.scrapped)
                raw_lots = raw_moves.mapped('quant_ids.lot_id')
            if not produced_lots:
                produced_moves = production.move_created_ids2.filtered(
                   lambda r: r.state == 'done' and not r.scrapped)
                produced_lots = produced_moves.mapped('quant_ids.lot_id')
            max_date = min(
                [max([x.use_date, x.extended_shelf_life_date])
                if x.product_expected_use == 'raw' else x.use_date
                for x in raw_lots if x.use_date]
                or [False]
            )
            for lot_id in produced_lots:
                today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                use_date = lot_id.use_date or today
                if check_production_lot_date_type == 'only_expired':
                    produced_moves = production.move_created_ids2.filtered(
                       lambda r: r.state == 'done' and not r.scrapped and r.date)
                    use_date = min(produced_moves.mapped('date') or [False]) or today
                max_date = max_date and max_date[:10] or False
                use_date = use_date and use_date[:10] or False
                if max_date and use_date > max_date:
                    body = _('Use date should be checked. The Serial Number/Lot will be locked.')
                    lot_id.message_post(body=body)
                    lot_id.sudo().lock_lot()

