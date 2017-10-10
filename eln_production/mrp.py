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
from openerp.osv import osv, fields
import time
from datetime import datetime, timedelta
from openerp import tools
from openerp.tools.translate import _
from openerp.addons.product import _common
from openerp.tools import float_compare, float_is_zero
import openerp.addons.decimal_precision as dp
from openerp import models, api
from openerp.tools.float_utils import float_round


class change_production_qty(osv.osv_memory):
    _inherit = 'change.production.qty'

    def _update_product_to_produce(self, cr, uid, prod, qty, context=None):
        res = super(change_production_qty, self)._update_product_to_produce(cr, uid, prod, qty, context=context)
        uom_obj = self.pool.get('product.uom')
        move_lines_obj = self.pool.get('stock.move')
        proc_obj = self.pool.get("procurement.order")
        for m in prod.move_created_ids:
            if m.product_uos:
                uos_qty = uom_obj._compute_qty(cr, uid, m.product_uom.id, qty, m.product_uos.id)
                move_lines_obj.write(cr, uid, [m.id], {'product_uos_qty': uos_qty})
        procs = proc_obj.search(cr, uid, [('production_id', '=', prod.id)], context=context)
        if procs:
            procurement = proc_obj.browse(cr, uid, procs, context=context)
            body = _('Manufacturing Order <em>%s</em> has changed the quantity: %s -> %s') % (procurement.production_id.name, procurement.product_qty, qty)
            proc_obj.message_post(cr, uid, procs, body=body, context=context)
            uos_qty = prod.product_uos and uom_obj._compute_qty(cr, uid, prod.product_uom.id, qty, prod.product_uos.id) or 0.0
            proc_obj.write(cr, uid, procs, {'product_qty': qty, 'product_uos_qty': uos_qty}, context=context)
        return res

    def change_prod_qty(self, cr, uid, ids, context=None):
        """ Cuando se cambia la cantidad debe volver a comprobar las reservas, pues si ya estaban hechas
        era para la cantidad anterior """
        res = super(change_production_qty, self).change_prod_qty(cr, uid, ids, context=context)
        record_id = context and context.get('active_id', False)
        assert record_id, _('Active Id not found')
        prod_obj = self.pool.get('mrp.production')
        move_obj = self.pool.get('stock.move')
        prod = prod_obj.browse(cr, uid, record_id, context=context)
        # Solo actuamos sobre los movimientos que ya tenían algo reservado
        # Si había sido forzada la disponibilidad o no se había reservado nunca lo dejamos como está
        move_ids = [x.id for x in prod.move_lines
                if x.state in ('confirmed', 'waiting', 'assigned') and len(x.reserved_quant_ids) > 0]
        move_obj.do_unreserve(cr, uid, move_ids, context=context)
        move_obj.action_assign(cr, uid, move_ids, context=context)
        return res

change_production_qty()


class mrp_workcenter(osv.osv):
    _inherit = 'mrp.workcenter'

    _columns = {
        'operators_ids': fields.many2many('hr.employee', 'hr_employee_mrp_workcenter_rel', 'workcenter_id', 'employee_id', string='Operators'),
    }

mrp_workcenter()


def rounding(f, r):
    import math
    if not r:
        return f
    return math.ceil(f / r) * r


class mrp_bom(osv.osv):
    _inherit = 'mrp.bom'

    _columns = {
        'alternatives_routing_ids': fields.many2many('mrp.routing', 'mrp_bom_routing_rel', 'bom_id', 'routing_id', string="Alternatives routings")
    }

    def _check_product(self, cr, uid, ids, context=None):
        return True

    _constraints = [
        (_check_product, 'BoM line product should not be same as BoM product.', ['product_id']),
    ]

    def _bom_explode(self, cr, uid, bom, product, factor, properties=None, level=0, routing_id=False, previous_products=None, master_bom=None, context=None):
        result, result2 = super(mrp_bom,self)._bom_explode(cr, uid, bom, product, factor, properties=None, level=0, routing_id=False, previous_products=None, master_bom=None, context=None)

        routing_obj = self.pool.get('mrp.routing')

        def _factor(factor, product_efficiency, product_rounding):
            factor = factor / (product_efficiency or 1.0)
            factor = _common.ceiling(factor, product_rounding)
            if factor < product_rounding:
                factor = product_rounding
            return factor

        def _get_vals(wc_use, operators, operators_n, factor, bom, wc, routing):
            qty_per_cycle = self.pool.get('product.uom')._compute_qty(cr, uid, wc_use.uom_id.id, wc_use.qty_per_cycle, bom.product_uom.id)
            oper = []
            if operators_n and operators:
                for op in range(0, (operators_n)):
                    oper.append(operators[op])
            return{
                'name': tools.ustr(wc_use.name) + u' - ' + tools.ustr(bom.product_id.name),
                'routing_id': routing.id,
                'workcenter_id': wc.id,
                'sequence': level + (wc_use.sequence or 0),
                'operators_ids': oper and [(6, 0, oper)] or False,
                'cycle': wc_use.cycle_nbr * (factor * bom.product_qty),
                'time_start': wc_use.time_start,
                'time_stop': wc_use.time_stop,
                'hour': float(((factor * bom.product_qty) * (wc_use.hour_nbr or 1.0) / (qty_per_cycle or 1.0)) * (wc.time_efficiency or 1.0)),
                'real_time': float(((factor * bom.product_qty) * (wc_use.hour_nbr or 1.0) / (qty_per_cycle or 1.0)) * (wc.time_efficiency or 1.0)),
            }

        factor = _factor(factor, bom.product_efficiency, bom.product_rounding)
        result2 = []

        routing = (routing_id and routing_obj.browse(cr, uid, routing_id)) or bom.routing_id or False
        if routing:
            for wc_use in routing.workcenter_lines:
                wc = wc_use.workcenter_id
                operators = []
                if wc_use.operators_ids:
                    for oper in wc_use.operators_ids:
                        operators.append(oper.id)
                result2.append(_get_vals(wc_use, operators, wc_use.operators_number, factor, bom, wc, routing))

        return result, result2


class mrp_routing_workcenter(osv.osv):
    _inherit = 'mrp.routing.workcenter'

    _columns = {
        'operators_ids': fields.many2many('hr.employee', 'hr_employee_mrp_routing_workcenter_rel', 'routing_workcenter_id', 'employee_id', string='Operators'),
        'capacity_per_cycle': fields.float('Capacity per Cycle', help="Number of operations this Work Center can do in parallel. If this Work Center represents a team of 5 workers, the capacity per cycle is 5."),
        'time_start': fields.float('Time before prod.', help="Time in hours for the setup."),
        'time_stop': fields.float('Time after prod.', help="Time in hours for the cleaning."),
        'qty_per_cycle': fields.float('Qty x cycle'),
        'uom_id': fields.many2one('product.uom', 'UoM'),
        'operators_number': fields.integer('Operators Nº')
    }

    def onchange_workcenter_id(self, cr, uid, ids, workcenter_id, context=None):
        """ Changes Operators if workcenter changes.
        @param workcenter_id: Changed workcenter_id
        @return:  Dictionary of changed values
        """
        if workcenter_id:
            operators = []
            workcenter = self.pool.get('mrp.workcenter').browse(cr, uid, workcenter_id, context=context)
            if workcenter.operators_ids:
                for oper in workcenter.operators_ids:
                    operators.append(oper.id)
                return {'value': {'operators_ids': operators}}
        return {}

mrp_routing_workcenter()


class production_stops(osv.osv):
    _name = 'production.stops'
    _columns = {
        'name': fields.char('Name',size=32, required=True),
        'reason': fields.char('Reason', size=255, required=True),
        'time': fields.float('Time', required=True),
        'production_workcenter_line_id': fields.many2one('mrp.production.workcenter.line', 'Production workcenter line')
    }


class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'

    def _read_group_workcenter_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        access_rights_uid = access_rights_uid or uid
        workcenter_obj = self.pool.get('mrp.workcenter')
        order = workcenter_obj._order
        if read_group_order == 'workcenter_id desc':
            # lame hack to allow reverting search, should just work in the trivial case
            order = "%s desc" % order
        workcenter_ids = workcenter_obj._search(cr, uid, [], order=order,
                                      access_rights_uid=access_rights_uid, context=context)
        result = workcenter_obj.name_get(cr, access_rights_uid, workcenter_ids, context=context)
        # restore order of the search
        result.sort(lambda x,y: cmp(workcenter_ids.index(x[0]), workcenter_ids.index(y[0])))
        return result, {}

    _group_by_full = {
        'workcenter_id': _read_group_workcenter_ids
    }

    def _get_color_stock(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        mvs = []
        moves = []
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            if line.product:
                moves = self.pool.get('stock.move').search(cr, uid, [('picking_type_id.code','=','outgoing'),('state','not in',('done','cancel'))])
                if moves:
                    for move in moves:
                        obj = self.pool.get('stock.move').browse(cr,uid, move)
                        if obj.date_expected[:10] == time.strftime('%Y-%m-%d'):
                            mvs.append(obj.id)
                if mvs and line.stock < 0:
                    res[line.id] = 2
                elif not mvs and line.stock < 0:
                    res[line.id] = 3
                elif line.stock > 0:
                    res[line.id] = 4
        return res

    def _get_date_stop(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = False
            if line.date_expected and line.hour:
                start = datetime.strptime(line.date_expected, "%Y-%m-%d %H:%M:%S")
                stop = start + timedelta(hours=line.hour)
                res[line.id] = stop.strftime("%Y-%m-%d %H:%M:%S")

        return res

    _columns = {
        'operators_ids': fields.many2many('hr.employee', 'hr_employee_mrp_prod_workc_line_rel', 'workcenter_line_id', 'employee_id', string='Operators'),
        'production_stops_ids': fields.one2many('production.stops', 'production_workcenter_line_id', 'Production Stops'),
        'time_start': fields.float('Time before prod.', help="Time in hours for the setup."),
        'time_stop': fields.float('Time after prod.', help="Time in hours for the cleaning."),
        'gasoleo_start': fields.float('Gasoleo start'),
        'gasoleo_stop': fields.float('Gasoleo stop'),
        'color': fields.integer('Color Index'),
        'move_id': fields.related('production_id', 'move_prod_id', type='many2one',relation='stock.move', string='Move', readonly=True),
        'date_expected': fields.related('move_id', 'date_expected', type='datetime', string='date', readonly=True),
        'date_stop': fields.function(_get_date_stop, type="datetime", string="Date stop", readonly=True),
        'stock': fields.related('product', 'real_virtual_available', type='float', string='Stock', readonly=True),
        'color_stock': fields.function(_get_color_stock, type="integer", string="Color stock", readonly=True),
        'routing_id': fields.many2one('mrp.routing', 'Routing', readonly=True),
        'real_time': fields.float('Real time'),
        'production_type': fields.related('production_id','production_type',
            type='selection',
            selection=[('normal','Normal'), ('rework','Rework'), ('sample','Sample'), ('special','Special')],
            string='Type of production', readonly=True),
    }

    def write(self, cr, uid, ids, vals, context=None, update=True):
        if not isinstance(ids, list):
            ids = [ids]
        for prod in self.browse(cr, uid, ids, context=context):
            if vals.get('workcenter_id', False):
                if prod.production_id.state <> 'validated' and update:
                    raise osv.except_osv(_("ERROR!"), _("You can not modify a work order associated at a production with a state other than 'validated'") )
        return super(mrp_production_workcenter_line, self).write(cr, uid, ids, vals, context=context)

    def modify_production_order_state(self, cr, uid, ids, action):
        """ Modifies production order state if work order state is changed.
        @param action: Action to perform.
        @return: Nothing
        """
        prod_obj_pool = self.pool.get('mrp.production')
        oper_obj = self.browse(cr, uid, ids)[0]
        prod_obj = oper_obj.production_id
        if action == 'start':
            if prod_obj.state =='confirmed':
                prod_obj_pool.force_production(cr, uid, [prod_obj.id])
                prod_obj_pool.signal_workflow(cr, uid, [prod_obj.id], 'button_produce')
            elif prod_obj.state in ('ready', 'in_production', 'finished', 'validated', 'closed'):
                prod_obj_pool.signal_workflow(cr, uid, [prod_obj.id], 'button_produce')
            else:
                raise osv.except_osv(_('Error!'),_('Manufacturing order cannot be started in state "%s"!') % (prod_obj.state,))
        else:
            return super(mrp_production_workcenter_line, self).modify_production_order_state(cr, uid, ids, action)
        return


class hrEmployee(models.Model):
    _inherit = 'hr.employee'

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        """ Display only operators of the workecenterlines of the
            mrp.production route"""
        if context is None:
            context = {}
        operator_ids = []
        if context.get('routing_id', False):
            t_rout = self.pool.get('mrp.routing')
            rout_obj = t_rout.browse(cr, uid, context['routing_id'], context)
            for line in rout_obj.workcenter_lines:
                if line.operators_ids:
                    for op in line.operators_ids:
                        operator_ids.append(op.id)
            args = [['id', 'in', operator_ids]]
        return super(hrEmployee, self).search(cr, uid, args,
                                              offset=offset,
                                              limit=limit,
                                              order=order,
                                              context=context,
                                              count=count)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """" Display only operators of the workecenterlines of the
            mrp.production route"""
        res = super(hrEmployee, self).name_search(name, args=args,
                                                  operator=operator,
                                                  limit=limit)
        if self._context.get('routing_id', False):
            args = args or []
            recs = self.search(args)
            res = recs.name_get()
        return res


class mrpRouting(models.Model):
    _inherit = 'mrp.routing'

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        """ Overwrite in order to search only routings ior alternative
        routings of the material list"""
        # import ipdb; ipdb.set_trace()
        if context is None:
            context = {}
        routing_ids = []
        if context.get('bom_id', False):
            t_bom = self.pool.get('mrp.bom')
            bom_obj = t_bom.browse(cr, uid, context['bom_id'], context)
            if bom_obj.routing_id:
                routing_ids.append(bom_obj.routing_id.id)
            for r in bom_obj.alternatives_routing_ids:
                routing_ids.append(r.id)
            args = [['id', 'in', routing_ids]]
        return super(mrpRouting, self).search(cr, uid, args,
                                              offset=offset,
                                              limit=limit,
                                              order=order,
                                              context=context,
                                              count=count)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """
        Display only routes defined in material list routes or alternative
        routes. Uses the overwrited search
        """
        res = super(mrpRouting, self).name_search(name, args=args,
                                                  operator=operator,
                                                  limit=limit)
        if self._context.get('bom_id', False):
            args = args or []
            recs = self.search(args)
            res = recs.name_get()
        return res


class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    def _get_workcenter_id(self, cr, uid, ids, name, args, context=None):
        res = {}
        for production in self.browse(cr, uid, ids, context=context):
            res[production.id] = production.routing_id and production.routing_id.workcenter_lines and production.routing_id.workcenter_lines[0].workcenter_id.id
        return res
    
    def _get_color_production(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if ids:
            for production in self.browse(cr, uid, ids, context=context):
                if production.priority == '0':   # Prioridad no urgente
                    res[production.id] = 4       # verde claro
                elif production.priority == '1': # Prioridad normal
                    res[production.id] = 3       # amarillo
                elif production.priority == '2': # Prioridad urgente
                    res[production.id] = 2       # rojo claro
                elif production.priority == '3': # Prioridad muy urgente
                    res[production.id] = 1       # gris
                else:
                    res[production.id] = 0       # blanco
        return res

    _columns = {
        'date_planned': fields.datetime('Scheduled Date', required=True, select=1, copy=False),  #  Avoid Readonly
        'routing_id': fields.many2one('mrp.routing', string='Routing', on_delete='set null', readonly=True, states={'draft':[('readonly',False)],'confirmed':[('readonly',False)],'ready':[('readonly',False)]}, help="The list of operations (list of work centers) to produce the finished product. The routing is mainly used to compute work center costs during operations and to plan future loads on work centers based on production plannification."),
        'date_end_planned': fields.datetime('Date end Planned'),
        'state': fields.selection([('draft','New'),('confirmed','Waiting Goods'),('ready','Ready to Produce'),('in_production','Production Started'),('finished', 'Finished'),('validated', 'Validated'),('closed', 'Closed'),('cancel','Cancelled'),('done','Done')],'State', readonly=True,
                                    help='When the production order is created the state is set to \'Draft\'.\n If the order is confirmed the state is set to \'Waiting Goods\'.\n If any exceptions are there, the state is set to \'Picking Exception\'.\
                                    \nIf the stock is available then the state is set to \'Ready to Produce\'.\n When the production gets started then the state is set to \'In Production\'.\n When the production is over, the state is set to \'Done\'.'),
        'note': fields.text('Notes'),
        'workcenter_lines': fields.one2many('mrp.production.workcenter.line', 'production_id', 'Work Centers Utilisation'),  # remove readonly state
        'origin': fields.char('Source Document', readonly=False,  states={'cancel':[('readonly', True)], 'done':[('readonly', True)]},
            help="Reference of the document that generated this production order request.", copy=False),
        'workcenter_id': fields.function(_get_workcenter_id, method=True, store=True, 
                                          type='many2one', relation='mrp.workcenter',
                                          string='Work Center', help="Work center of the first operation of the route."), #Uso para operaciones de agrupacion, filtrado, etc.
        'color_production': fields.function(_get_color_production, type="integer", string="Color production", readonly=True),
        'theo_cost': fields.float('Theorical Cost', digits=(16,6), copy=False), # Coste teórico unitario producto terminado al momento de realizar la producción
        'sequence': fields.integer('Sequence', help="Used to order the production planning kanban view"),
        'production_type': fields.selection([('normal','Normal'), ('rework','Rework'), ('sample','Sample'), ('special','Special')], 'Type of production'),
    }
    _defaults = {
        'production_type': 'normal',
    }
    _order = 'name desc'

    def modify_consumption(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        else:
            context = context.copy()
        context.update({
            'active_model': self._name,
            'active_ids': ids,
            'active_id': ids[0]
        })
        created_id = self.pool['mrp.modify.consumption'].create(cr, uid, {}, context)
        return self.pool['mrp.modify.consumption'].wizard_view(cr, uid, created_id, context)

    def _costs_generate(self, cr, uid, production):
        """ Calculates total costs at the end of the production.
        @param production: Id of production order.
        @return: Calculated amount.
        """
        amount = 0.0
        analytic_line_obj = self.pool.get('account.analytic.line')
        for wc_line in production.workcenter_lines:
            wc = wc_line.workcenter_id
            if wc.costs_journal_id and wc.costs_general_account_id:
                # Cost per hour
                value = wc_line.hour * wc.costs_hour
                account = wc.costs_hour_account_id.id
                if value and account:
                    amount += value
                    analytic_line_obj.create(cr, uid, {
                        'name': wc_line.name + ' (H)',
                        'amount': value,
                        'account_id': account,
                        'general_account_id': wc.costs_general_account_id.id,
                        'journal_id': wc.costs_journal_id.id,
                        'ref': wc.code,
                        'product_id': wc.product_id.id,
                        'unit_amount': wc_line.hour,
                        'product_uom_id': wc.product_id and wc.product_id.uom_id.id or False
                    } )

        return amount

    def _make_production_produce_line(self, cr, uid, production, context=None):
        move_id = super (mrp_production, self)._make_production_produce_line(cr, uid, production, context=context)
        #Lo cambio para no sobreescribir toda la función
        stock_move = self.pool.get('stock.move')
        stock_move_id = stock_move.browse(cr, uid, move_id)
        move_name = _('PROD: %s') % production.name
        stock_move_id.write({'name' : move_name})

        if production.product_id and production.product_id.sample_location:
            location = self.pool.get('stock.location')
            destloc = location.search(cr, uid, [('sample_location', '=', True)])
            if destloc:
                destination_location_id = destloc[0]
                source_location_id = production.product_id.product_tmpl_id.property_stock_production.id
                data = {
                    'name': move_name,
                    'date': production.date_planned,
                    'product_id': production.product_id.id,
                    'product_uom_qty': production.product_id.qty_sample,
                    'product_uom': production.product_uom.id,
                    'product_uos_qty': production.product_uos and production.product_uos_qty or False,
                    'product_uos': production.product_uos and production.product_uos.id or False,
                    'location_id': source_location_id,
                    'location_dest_id': destination_location_id,
                    'procurement_id': stock_move_id.procurement_id,
                    'company_id': production.company_id.id,
                    'production_id': production.id,
                    'origin': production.name,
                    'group_id': stock_move_id.group_id,
                    }
                move = stock_move.create(cr, uid, data, context=context)
                stock_move.action_confirm(cr, uid, [move], context=context)
        return move_id

    def product_qty_change(self, cr, uid, ids, product_id, product_qty, product_uom, product_uos, context=None):
        result = {'value': {}}
        if product_id:
            product_obj = self.pool.get('product.product').browse(cr, uid, product_id)
            if product_uos:
                if self.pool.get('product.uom').browse(cr, uid, product_uos).category_id.id == product_obj.uos_id.category_id.id:
                    if product_qty:
                        if product_obj.uos_coeff:
                            qty_uos = float(product_qty * product_obj.uos_coeff)
                            result['value']['product_uos_qty'] = qty_uos
        return result

    def product_uos_qty_change(self, cr, uid, ids, product_id, product_uos_qty, product_uos, product_uom, context=None):
        result = {'value': {}}
        if product_id:
            product_obj = self.pool.get('product.product').browse(cr, uid, product_id)
            if product_uom:
                if self.pool.get('product.uom').browse(cr, uid, product_uom).category_id.id == product_obj.uom_id.category_id.id:
                    if product_uos_qty:
                        if product_obj.uos_coeff:
                            qty_uom = float(product_uos_qty / product_obj.uos_coeff)
                            result['value']['product_qty'] = qty_uom
        return result

    def bom_id_change(self, cr, uid, ids, bom_id, context=None):
        """ Finds routing for changed BoM.
        @param product: Id of product.
        @return: Dictionary of values.
        """

        result = super(mrp_production,self).bom_id_change(cr, uid, ids, bom_id, context=context)
        if not bom_id:
            return {'value': {
                'ids_str': "[]"
            }}
        bom_point = self.pool.get('mrp.bom').browse(cr, uid, bom_id, context=context)
        stream = []
        result['value']['ids_str'] = "[]"
        if bom_point.routing_id:
            stream.append(str(bom_point.routing_id.id))
        if bom_point.alternatives_routing_ids:
            for line in bom_point.alternatives_routing_ids:
                stream.append(str(line.id))
        if stream:
            result['value']['ids_str2'] =  "[" + u", ".join(stream) + "]"

        return result

    def action_produce(self, cr, uid, production_id, production_qty, production_mode, wiz=False, context=None):
        if context is None:
            context = {}
        context = dict(context)
        stock_mov_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get("product.uom")
        production = self.browse(cr, uid, production_id, context=context)
        production_qty_uom = uom_obj._compute_qty(cr, uid, production.product_uom.id, production_qty, production.product_id.uom_id.id)
        precision = self.pool['decimal.precision'].precision_get(cr, uid, 'Product Unit of Measure')

        main_production_move = False
        if production_mode == 'produce':  # New Case: Produce Only
            produced_products = {}
            for produced_product in production.move_created_ids2:
                if produced_product.scrapped:
                    continue
                if not produced_products.get(produced_product.product_id.id, False):
                    produced_products[produced_product.product_id.id] = 0
                produced_products[produced_product.product_id.id] += produced_product.product_qty

            for produce_product in production.move_created_ids:
                subproduct_factor = self._get_subproduct_factor(cr, uid, production.id, produce_product.id, context=context)
                lot_id = False
                if wiz:
                    lot_id = wiz.lot_id.id
                qty = min(subproduct_factor * production_qty_uom, produce_product.product_qty) #Needed when producing more than maximum quantity
                new_moves = stock_mov_obj.action_consume(cr, uid, [produce_product.id], qty,
                                                         location_id=produce_product.location_id.id, restrict_lot_id=lot_id, context=context)
                stock_mov_obj.write(cr, uid, new_moves, {'production_id': production_id}, context=context)
                remaining_qty = subproduct_factor * production_qty_uom - qty
                if not float_is_zero(remaining_qty, precision_digits=precision):
                    # In case you need to make more than planned
                    # consumed more in wizard than previously planned
                    extra_move_id = stock_mov_obj.copy(cr, uid, produce_product.id, default={'product_uom_qty': remaining_qty,
                                                                                             'production_id': production_id}, context=context)
                    stock_mov_obj.action_confirm(cr, uid, [extra_move_id], context=context)
                    stock_mov_obj.action_done(cr, uid, [extra_move_id], context=context)

                if produce_product.product_id.id == production.product_id.id:
                    main_production_move = produce_product.id

            if not production.move_created_ids and \
                not (context.get('default_mode', False) and context['default_mode'] == 'consume'):
                self.signal_workflow(cr, uid, [production_id], 'button_finished_validated')
        else:
            if not main_production_move:
                main_production_move = production.move_created_ids2 and production.move_created_ids2[0].id
            context.update({'main_production_move': main_production_move})  # Para escribirlo en el write y en el action_consume()
            res = super(mrp_production, self).action_produce(cr, uid, production_id, production_qty, production_mode, wiz=wiz, context=context)
            if not production.move_created_ids and \
                not (context.get('default_mode', False) and context['default_mode'] == 'consume'):
                self.signal_workflow(cr, uid, [production_id], 'button_finished_validated')
            if context.get('default_mode', False) and context['default_mode'] == 'consume':  # Custom behaivor, set closed state
                self.signal_workflow(cr, uid, [production_id], 'button_validated_closed')

        return True

    def action_finished(self, cr, uid, ids, context=None):
        print "action_finished"
        for production in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, production.id, {'state': 'finished'})
        return True

    def action_validated(self, cr, uid, ids, context=None):
        print "action_validate"
        tmpl_obj = self.pool.get('product.template')
        for production in self.browse(cr, uid, ids, context=context):
            bom = production.bom_id
            theo_cost = tmpl_obj._calc_price(cr, uid, bom, test=True, context=context)
            self.write(cr, uid, production.id, {'state': 'validated', 'theo_cost': theo_cost})
        return True

    def action_close(self, cr, uid, ids, context=None):
        print "action_close"
        tmpl_obj = self.pool.get('product.template')
        precision = self.pool['decimal.precision'].precision_get(cr, uid, 'Product Price')
        for production in self.browse(cr, uid, ids, context=context):
            date = max([x.date
                        for x in production.move_created_ids2
                        if x.state == 'done' and not x.scrapped] or [None])
            for move in production.move_lines2.filtered(lambda r: r.state == 'done'):
                # Establecemos en los movimiento de consumos los precios de coste de producto que tenía en la fecha
                # que se realizó el producto finalizado, para que coincida con la misma posición
                # en la que se calcula el theo_cost. Esto es debido a que los consumos se pueden hacer más
                # tarde que la validación del producto terminado (action_validated)
                price_unit = tmpl_obj.get_history_price(cr, uid, move.product_id.product_tmpl_id.id,
                                                        move.company_id.id,
                                                        date=date)
                # Aplicamos el redondeo que tendría el campo standard_price,
                # ya que get_history_price devuelve el valor sin precision
                price_unit = float_round(price_unit, precision_digits=precision) 
                price_unit = price_unit or move.product_id.standard_price
                move.write({'price_unit': price_unit})
            self.write(cr, uid, production.id, {'state': 'closed'})
        return True

    def action_recalculate_time(self, cr, uid, ids, properties=[],context=None):
        workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')
        for production in self.browse(cr, uid, ids):
            time = 0.00
            if production.workcenter_lines:
                for line in production.workcenter_lines:
                    if line.operators_ids:
                        real_operators = len([x.id for x in line.operators_ids])
                        real_qty = line.qty
                        wc = self.pool.get('mrp.routing.workcenter').search(cr, uid, [('routing_id','=',production.routing_id.id), ('workcenter_id','=',line.workcenter_id.id),('sequence','=',line.sequence)])
                        if wc:
                            wco = self.pool.get('mrp.routing.workcenter').browse(cr, uid, wc[0])
                            obj_operators = wco.operators_number
                            obj_qty = wco.qty_per_cycle
                            time = float((obj_operators * (real_qty/obj_qty or 1.0))/(real_operators or 1.0))
                            workcenter_line_obj.write(cr, uid, line.id, {'real_time': time})
                        else:
                            raise osv.except_osv(_('Error!'),  _('Can not recalculate time because not exists objectives datas in the lines of the routing'))
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        """ Cancels the production order and related stock moves.
        @return: True
        """
        if context is None:
            context = {}

        res = super(mrp_production, self).action_cancel(cr, uid, ids, context=context)
        if res:
            # Put related procurements in cancel state
            proc_obj = self.pool.get("procurement.order")
            procs = proc_obj.search(cr, uid, [('production_id', 'in', ids)], context=context)
            if procs:
                proc_obj.write(cr, uid, procs, {'state': 'cancel'}, context=context)
        return res

    def action_in_production(self, cr, uid, ids, context=None):
        """
        Overwrite to set startworking state of all workcenter lines instead
        only one.
        """
        workcenter_pool = self.pool.get('mrp.production.workcenter.line')
        for prod in self.browse(cr, uid, ids):
            if prod.workcenter_lines:
                workcenter_pool.signal_workflow(cr, uid, [x.id for x in prod.workcenter_lines], 'button_start_working')
        return super(mrp_production, self).action_in_production(cr, uid, ids, context=context)

    def action_production_end(self, cr, uid, ids, context=None):
        uom_obj = self.pool.get("product.uom")
        bom_obj = self.pool.get("mrp.bom")
        prod_line_obj = self.pool.get('mrp.production.product.line')
        res = super(mrp_production, self).\
            action_production_end(cr, uid, ids, context=context)
        for prod in self.browse(cr, uid, ids, context=context):
            bom = prod.bom_id
            finished_qty = sum([x.product_uom_qty
                                for x in prod.move_created_ids2 
                                if x.state == 'done' and not x.scrapped])
            factor = uom_obj._compute_qty(cr, uid, prod.product_uom.id,
                                          finished_qty,
                                          bom.product_uom.id)
            new_qty = factor / bom.product_qty
            routing_id = prod.routing_id.id
            res = bom_obj._bom_explode(cr, uid, bom, prod.product_id,
                                       new_qty, routing_id=routing_id)
            prod_lines = res[0]
            prod.product_lines.unlink()
            for line in prod_lines:
                line['production_id'] = prod.id
                prod_line_obj.create(cr, uid, line)
        return res

    def unlink(self, cr, uid, ids, context=None):
        """ Unlink the production order and related stock moves.
        @return: True
        """
        res = {}
        if context is None:
            context = {}

        move_obj = self.pool.get('stock.move')

        if any(x.state not in ('draft', 'confirmed', 'ready', 'in_production', 'cancel') for x in self.browse(cr, uid, ids, context=context)):
            raise osv.except_osv(_('Error!'),  _('You cannot delete a production which is not cancelled.'))
        
        for production in self.browse(cr, uid, ids, context=context):
            if production.state in ('draft', 'confirmed', 'ready', 'in_production'):
                self.action_cancel(cr, uid, [production.id], context=context)
            if production.state == 'cancel':
                move_obj.unlink(cr, uid, [x.id for x in production.move_created_ids2], context=context)
                move_obj.unlink(cr, uid, [x.id for x in production.move_lines2], context=context)
                res = super(mrp_production, self).unlink(cr, uid, [production.id], context=context)
            else:
                raise osv.except_osv(_('Error!'),  _('You cannot delete a production which is not cancelled.'))

        return res

mrp_production()
