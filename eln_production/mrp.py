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
from openerp import netsvc
#from openerp.tools import float_compare
from operator import attrgetter
from openerp.addons.product import _common

class change_production_qty(osv.osv_memory):
    _inherit = 'change.production.qty'

    def change_prod_qty(self, cr, uid, ids, context=None):
        res = super(change_production_qty, self).change_prod_qty(cr, uid, ids, context=context)
        prod_obj = self.pool.get('mrp.production')
        record_id = context and context.get('active_id',False)
        assert record_id, _('Active Id is not found')
        for wiz_qty in self.browse(cr, uid, ids, context=context):
            prod = prod_obj.browse(cr, uid, record_id, context=context)
            if prod.product_uom and prod.product_uos and prod.product_uos.id == prod.product_id.uos_id.id:
                prod_obj.write(cr, uid, prod.id, {'product_uos_qty': wiz_qty.product_qty * (prod.product_id.uos_coeff or 1.0)})

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
    def _bom_explode_bis(self, cr, uid, bom, product, factor, properties=None, level=0, routing_id=False, previous_products=None, master_bom=None, context=None):



        """ Finds Products and Work Centers for related BoM for manufacturing order.
        @param bom: BoM of particular product template.
        @param product: Select a particular variant of the BoM. If False use BoM without variants.
        @param factor: Factor represents the quantity, but in UoM of the BoM, taking into account the numbers produced by the BoM
        @param properties: A List of properties Ids.
        @param level: Depth level to find BoM lines starts from 10.
        @param previous_products: List of product previously use by bom explore to avoid recursion
        @param master_bom: When recursion, used to display the name of the master bom
        @return: result: List of dictionaries containing product details.
                 result2: List of dictionaries containing Work Center details.
        """
        result, result2 = super(mrp_bom, self)._bom_explode\
                (self, cr, uid, bom, product, factor, properties=None, level=0, routing_id=False, previous_products=None, master_bom=None, context=None)



        #SI ES PHANTOM SUSTITUYE PRODUCTO POR LISTA DE MATERIALES
        ##
                ## Estaba así
                # def _bom_explode(self, cr, uid, bom, factor, properties=[], addthis=False, level=0, routing_id=False):
                # """ Finds Products and Work Centers for related BoM for manufacturing order.
                # @param bom: BoM of particular product.
                # @param factor: Factor of product UoM.
                # @param properties: A List of properties Ids.
                # @param addthis: If BoM found then True else False.
                # @param level: Depth level to find BoM lines starts from 10.
                # @return: result: List of dictionaries containing product details.
                #          result2: List of dictionaries containing Work Center details.
                # """
        def _get_vals(wc_use, operators, operators_n, factor, bom, wc, routing):

            qty_per_cycle = self.pool.get('product.uom')._compute_qty(cr, uid, wc_use.uom_id.id, wc_use.qty_per_cycle, bom.product_uom.id)
            oper = []
            if operators_n and operators:
                for op in range(0, (operators_n)):
                    oper.append(operators[op])
            return{
                'name': tools.ustr(wc_use.name) + u' - '  + tools.ustr(bom.product_id.name),
                'routing_id': routing.id,
                'workcenter_id': wc.id,
                'sequence': level+(wc_use.sequence or 0),
                'operators_ids': oper and [(6,0,oper)] or False,
                'cycle': wc_use.cycle_nbr * (factor * bom.product_qty),
                'time_start': wc_use.time_start,
                'time_stop': wc_use.time_stop,
                'hour': float((wc_use.operators_number * ((factor * bom.product_qty)/(qty_per_cycle or 1.0)))/(operators_n or 1.0)),
                'real_time': float((wc_use.operators_number * ((factor * bom.product_qty)/(qty_per_cycle or 1.0)))/(operators_n or 1.0))

                    }

        routing = (routing_id and routing_obj.browse(cr, uid, routing_id)) or bom.routing_id or False
        if routing:
            for wc_use in routing.workcenter_lines:
                wc = wc_use.workcenter_id
                d, m = divmod(factor, wc_use.workcenter_id.capacity_per_cycle)
                mult = (d + (m and 1.0 or 0.0))
                cycle = mult * wc_use.cycle_nbr
                result2.append({
                    'name': tools.ustr(wc_use.name) + ' - ' + tools.ustr(bom.product_tmpl_id.name_get()[0][1]),
                    'workcenter_id': wc.id,
                    'sequence': level + (wc_use.sequence or 0),
                    'cycle': cycle,
                    'hour': float(wc_use.hour_nbr * mult + ((wc.time_start or 0.0) + (wc.time_stop or 0.0) + cycle * (wc.time_cycle or 0.0)) * (wc.time_efficiency or 1.0)),
                })
        routing_obj = self.pool.get('mrp.routing')
        factor = factor / (bom.product_efficiency or 1.0)
        factor = rounding(factor, bom.product_rounding)
        if factor < bom.product_rounding:
            factor = bom.product_rounding
        result = []
        result2 = []
        phantom = False
        if bom.type == 'phantom' and not bom.bom_line_ids:
                    # #def _bom_find(self, cr, uid, product_tmpl_id=None, product_id=None, properties=None, context=None):
                    # """
                    # Finds BoM for particular product and product uom.
                    # @param product_tmpl_id: Selected product.
                    # @param product_uom: Unit of measure of a product.
                    # @param properties: List of related properties.
                    # @return: False or BoM id
                    # newbom = self._bom_find(cr, uid, bom.product_id.id, bom.product_uom.id, properties)
                    # """
            newbom = self._bom_find(cr, uid, bom.product_tmpl_id.id, bom.product_id.id, properties)

            if newbom:
                res = self._bom_explode(cr, uid, self.browse(cr, uid, [newbom])[0], factor*bom.product_qty, properties, level=level+10)
                result = result + res[0]
                result2 = result2 + res[1]
                phantom = True
            else:
                phantom = False
        if not phantom:
            if newbom and not bom.bom_lines_ids:
                result.append(
                {
                    'name': bom.product_id.name,
                    'product_id': bom.product_id.id,
                    'product_qty': bom.product_qty * factor,
                    'product_uom': bom.product_uom.id,
                    'product_uos_qty': bom.product_uos and bom.product_uos_qty * factor or False,
                    'product_uos': bom.product_uos and bom.product_uos.id or False,
                })
            routing = (routing_id and routing_obj.browse(cr, uid, routing_id)) or bom.routing_id or False
            if routing:
                for wc_use in routing.workcenter_lines:
                    wc = wc_use.workcenter_id
                    operators = []
                    if wc_use.operators_ids:
                        for oper in wc_use.operators_ids:
                            operators.append(oper.id)
                    result2.append(_get_vals(wc_use, operators, wc_use.operators_number, factor, bom, wc, routing))

            for bom2 in bom.bom_lines:
                res = self._bom_explode(cr, uid, bom2, factor, properties, level=level+10)
                result = result + res[0]
                result2 = result2 + res[1]
        return result, result2

    def _bom_explode(self, cr, uid, bom, product, factor, properties=None, level=0, routing_id=False, previous_products=None, master_bom=None, context=None):
        """ Finds Products and Work Centers for related BoM for manufacturing order.
        @param bom: BoM of particular product template.
        @param product: Select a particular variant of the BoM. If False use BoM without variants.
        @param factor: Factor represents the quantity, but in UoM of the BoM, taking into account the numbers produced by the BoM
        @param properties: A List of properties Ids.
        @param level: Depth level to find BoM lines starts from 10.
        @param previous_products: List of product previously use by bom explore to avoid recursion
        @param master_bom: When recursion, used to display the name of the master bom
        @return: result: List of dictionaries containing product details.
                 result2: List of dictionaries containing Work Center details.
        """

        #TODO ESTA FUNCION HAY QUE REVISARLA. ESTA SOBREESCRITA.
        uom_obj = self.pool.get("product.uom")
        routing_obj = self.pool.get('mrp.routing')
        master_bom = master_bom or bom

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
                'name': tools.ustr(wc_use.name) + u' - '  + tools.ustr(bom.product_id.name),
                'routing_id': routing.id,
                'workcenter_id': wc.id,
                'sequence': level+(wc_use.sequence or 0),
                'operators_ids': oper and [(6,0,oper)] or False,
                'cycle': wc_use.cycle_nbr * (factor * bom.product_qty),
                'time_start': wc_use.time_start,
                'time_stop': wc_use.time_stop,
                'hour': float((wc_use.operators_number * ((factor * bom.product_qty)/(qty_per_cycle or 1.0)))/(operators_n or 1.0)),
                'real_time': float((wc_use.operators_number * ((factor * bom.product_qty)/(qty_per_cycle or 1.0)))/(operators_n or 1.0))
            }

        factor = _factor(factor, bom.product_efficiency, bom.product_rounding)

        result = []
        result2 = []

        routing = (routing_id and routing_obj.browse(cr, uid, routing_id)) or bom.routing_id or False
        if routing:
            for wc_use in routing.workcenter_lines:
                wc = wc_use.workcenter_id
                operators = []
                if wc_use.operators_ids:
                    for oper in wc_use.operators_ids:
                        operators.append(oper.id)
                #SE CAMBIA E SE AÑADE LA FUNCION _GET_VALS
                result2.append(_get_vals(wc_use, operators, wc_use.operators_number, factor, bom, wc, routing))

        for bom_line_id in bom.bom_line_ids:

            if self._skip_bom_line(cr, uid, bom_line_id, product, context=context):
                continue
            if set(map(int, bom_line_id.property_ids or [])) - set(properties or []):
                continue

            if previous_products and bom_line_id.product_id.product_tmpl_id.id in previous_products:
                raise osv.except_osv(_('Invalid Action!'), _('BoM "%s" contains a BoM line with a product recursion: "%s".') % (master_bom.name,bom_line_id.product_id.name_get()[0][1]))

            quantity = _factor(bom_line_id.product_qty * factor, bom_line_id.product_efficiency, bom_line_id.product_rounding)
            bom_id = self._bom_find(cr, uid, product_id=bom_line_id.product_id.id, properties=properties, context=context)
            #If BoM should not behave like PhantoM, just add the product, otherwise explode further
            #para este caso, siempre que unproducto tenga bom_id, deberemos de tratarlo como phantom (lo hacía antes así)
            bom_line_type = False
            if bom_id:
                bom_line_type = bom_line_id.type
                bom_line_id.type = "phantom"

            if bom_line_id.type != "phantom" and (not bom_id or self.browse(cr, uid, bom_id, context=context).type != "phantom"):
                result.append({
                    'name': bom_line_id.product_id.name,
                    'product_id': bom_line_id.product_id.id,
                    'product_qty': quantity,
                    'product_uom': bom_line_id.product_uom.id,
                    'product_uos_qty': bom_line_id.product_uos and _factor(bom_line_id.product_uos_qty * factor, bom_line_id.product_efficiency, bom_line_id.product_rounding) or False,
                    'product_uos': bom_line_id.product_uos and bom_line_id.product_uos.id or False,
                })
            elif bom_id:
                all_prod = [bom.product_tmpl_id.id] + (previous_products or [])
                bom2 = self.browse(cr, uid, bom_id, context=context)
                # We need to convert to units/UoM of chosen BoM
                factor2 = uom_obj._compute_qty(cr, uid, bom_line_id.product_uom.id, quantity, bom2.product_uom.id)
                quantity2 = factor2 / bom2.product_qty
                res = self._bom_explode(cr, uid, bom2, bom_line_id.product_id, quantity2,
                    properties=properties, level=level + 10, previous_products=all_prod, master_bom=master_bom, context=context)
                result = result + res[0]
                result2 = result2 + res[1]
            else:
                raise osv.except_osv(_('Invalid Action!'), _('BoM "%s" contains a phantom BoM line but the product "%s" does not have any BoM defined.') % (master_bom.name,bom_line_id.product_id.name_get()[0][1]))

            if bom_id:
                bom_line_id.type = bom_line_type
        return result, result2


mrp_bom()

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
    
production_stops()

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
        return result

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
                moves = self.pool.get('stock.move').search(cr, uid, [('product_id','=',line.product.id),('picking_id.type','=','out'),('state','not in',('done','cancel'))])
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
        'address': fields.related('move_id', 'address_id', type='many2one', string='address', relation='res.partner.address', readonly=True),
        'partnerid': fields.related('address', 'partner_id', type='many2one', string='Partner', relation='res.partner',readonly=True),
        'partner_name': fields.related('partnerid', 'name', type='char', string='Parntername', readonly=True),
        'date_expected': fields.related('move_id', 'date_expected', type='datetime', string='date', readonly=True),
        'date_stop': fields.function(_get_date_stop, type="datetime", string="Date stop", readonly=True),
        'stock': fields.related('product', 'real_virtual_available', type='float', string='Stock', readonly=True),
        'color_stock': fields.function(_get_color_stock, type="integer", string="Color stock", readonly=True),
        'routing_id': fields.many2one('mrp.routing', 'Routing', readonly=True),
        'real_time': fields.float('Real time'),

    }

    def write(self, cr, uid, ids, vals, context=None, update=True):
        if not isinstance(ids, list):
            ids = [ids]
        prod_obj = self.pool.get('mrp.production')
        for prod in self.browse(cr, uid, ids, context=context):
            if vals.get('workcenter_id', False):
                if prod.production_id.state <> 'validated' and update:
                    raise osv.except_osv(_("ERROR!"), _("You can not modify a work order associated at a production with a state other than 'validated'") )
        return super(mrp_production_workcenter_line, self).write(cr, uid, ids, vals, context=context)


mrp_production_workcenter_line()

class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    def _get_ids_str(self, cr, uid, ids, field_name, args, context=None):
        if context is None:
            context = {}
        res = {}

        for cur_obj in self.browse(cr, uid, ids):
            stream = []
            res[cur_obj.id] = "[]"
            if cur_obj.bom_id:
                bom_point = self.pool.get('mrp.bom').browse(cr, uid, cur_obj.bom_id.id, context=context)
                if bom_point.routing_id or bom_point.alternatives_routing_ids:
                    if bom_point.routing_id:
                        stream.append(str(bom_point.routing_id.id))
                    if bom_point.alternatives_routing_ids:
                        for line in bom_point.alternatives_routing_ids:
                            stream.append(str(line.id))
                    res[cur_obj.id] = "[" + u", ".join(stream) + "]"

        return res

    def _get_operator_ids_str(self, cr, uid, ids, field_name, args, context=None):
        if context is None:
            context = {}
        res = {}

        for cur_obj in self.browse(cr, uid, ids):
            stream = []
            res[cur_obj.id] = "[]"
            if cur_obj.routing_id:
                if cur_obj.routing_id.workcenter_lines:
                    for line in cur_obj.routing_id.workcenter_lines:
                        if line.operators_ids:
                            for op in line.operators_ids:
                                stream.append(str(op.id))

                    res[cur_obj.id] = "[" + u", ".join(stream) + "]"

        return res

    _columns = {
        'ids_str2': fields.function(_get_ids_str, method=True, string='ids_str', type='char', size=255),
        'operator_ids_str': fields.function(_get_operator_ids_str, method=True, string="Operators_ids_str", type="char", size=255),
        'routing_id': fields.many2one('mrp.routing', string='Routing', on_delete='set null', readonly=True, states={'draft':[('readonly',False)],'confirmed':[('readonly',False)],'ready':[('readonly',False)]}, help="The list of operations (list of work centers) to produce the finished product. The routing is mainly used to compute work center costs during operations and to plan future loads on work centers based on production plannification."),
        'date_end_planned': fields.datetime('Date end Planned'),
        'state': fields.selection([('draft','New'),('picking_except', 'Picking Exception'),('confirmed','Waiting Goods'),('ready','Ready to Produce'),('in_production','Production Started'),('finished', 'Finished'),('validated', 'Validated'),('closed', 'Closed'),('cancel','Cancelled'),('done','Done'),('reopen', 'Reopen')],'State', readonly=True,
                                    help='When the production order is created the state is set to \'Draft\'.\n If the order is confirmed the state is set to \'Waiting Goods\'.\n If any exceptions are there, the state is set to \'Picking Exception\'.\
                                    \nIf the stock is available then the state is set to \'Ready to Produce\'.\n When the production gets started then the state is set to \'In Production\'.\n When the production is over, the state is set to \'Done\'.'),
        'note': fields.text('Notes', readonly = False, states={'cancel':[('readonly', True)], 'done':[('readonly', True)]}),
    }
    
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
        stock_move = self.pool.get('stock.move')
        location = self.pool.get('stock.location')
        source_location_id = production.product_id.product_tmpl_id.property_stock_production.id
        destination_location_id = production.location_dest_id.id
        move_name = _('PROD: %s') % production.name
        data = {
            'name': move_name,
            'date': production.date_planned,
            'product_id': production.product_id.id,
            'product_qty': production.product_qty,
            'product_uom': production.product_uom.id,
            'product_uos_qty': production.product_uos and production.product_uos_qty or False,
            'product_uos': production.product_uos and production.product_uos.id or False,
            'location_id': source_location_id,
            'location_dest_id': destination_location_id,
            'move_dest_id': production.move_prod_id.id,
            'state': 'waiting',
            'company_id': production.company_id.id,
        }
        move_id = stock_move.create(cr, uid, data, context=context)
        production.write({'move_created_ids': [(6, 0, [move_id])]}, context=context)

        if production.product_id and production.product_id.sample_location:
            destloc = location.search(cr, uid, [('sample_location', '=', True)])
            if destloc:
                destination_location_id = destloc[0]
                source_location_id = production.product_id.product_tmpl_id.property_stock_production.id
                move_name = _('PROD: %s') % production.name
                data2 = {
                    'name': move_name,
                    'date': production.date_planned,
                    'product_id': production.product_id.id,
                    'product_qty': production.product_id.qty_sample,
                    'product_uom': production.product_uom.id,
                    'product_uos_qty': production.product_uos and production.product_uos_qty or False,
                    'product_uos': production.product_uos and production.product_uos.id or False,
                    'location_id': source_location_id,
                    'location_dest_id': destination_location_id,
                    'move_dest_id': production.move_prod_id.id,
                    'state': 'waiting',
                    'company_id': production.company_id.id,
                }
                move = stock_move.create(cr, uid, data2, context=context)
                production.write({'move_created_ids': [(6, 0, [move_id,move])]}, context=context)
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

    def product_id_change(self, cr, uid, ids, product_id, context=None):
        """ Finds UoM of changed product.
        @param product_id: Id of changed product.
        @return: Dictionary of values.
        """
        result = super(mrp_production,self).product_id_change(cr, uid, ids, product_id, context=context)
        if not product_id:
            return {'value': {
                'ids_str': u"[]",
                'product_uos': False
            }}
        product = self.pool.get('product.product'). browse(cr, uid, product_id, context=context)
        result['value']['product_uos'] = product.uos_id and product.uos_id.id or False

        if result['value'].get('bom_id', False):
            stream = []
            result['value']['ids_str2'] = u"[]"

            bom_point = self.pool.get('mrp.bom').browse(cr, uid, result['value']['bom_id'])
            if bom_point.routing_id:
                stream.append(str(bom_point.routing_id.id))
            if bom_point.alternatives_routing_ids:
                for line in bom_point.alternatives_routing_ids:
                    stream.append(str(line.id))
            if stream:
                result['value']['ids_str2'] =  u"[" + u", ".join(stream) + u"]"

        return result

    def action_produce(self, cr, uid, production_id, production_qty, production_mode, flag='', context=None):
        """ To produce final product based on production mode (consume/consume&produce).
        If Production mode is consume, all stock move lines of raw materials will be done/consumed.
        If Production mode is consume & produce, all stock move lines of raw materials will be done/consumed
        and stock move lines of final product will be also done/produced.
        @param production_id: the ID of mrp.production object
        @param production_qty: specify qty to produce
        @param production_mode: specify production mode (consume/consume&produce).
        @return: True
        """
        stock_mov_obj = self.pool.get('stock.move')
        production = self.browse(cr, uid, production_id, context=context)
        produced_qty = 0
        wf_service = netsvc.LocalService("workflow")
        for produced_product in production.move_created_ids2:
            if (produced_product.scrapped) or (produced_product.product_id.id <> production.product_id.id):
                continue
            produced_qty += produced_product.product_qty
        if flag == 'consume':
            if production_mode in ['consume','consume_produce']:
                consumed_data = {}

                # Calculate already consumed qtys
                for consumed in production.move_lines2:
                    if consumed.scrapped:
                        continue
                    if not consumed_data.get(consumed.product_id.id, False):
                        consumed_data[consumed.product_id.id] = 0
                    consumed_data[consumed.product_id.id] += consumed.product_qty

                # Find product qty to be consumed and consume it
                for scheduled in production.product_lines:

                    # total qty of consumed product we need after this consumption
                    total_consume = ((production_qty + produced_qty) * scheduled.product_qty / production.product_qty)

                    # qty available for consume and produce
                    qty_avail = scheduled.product_qty - consumed_data.get(scheduled.product_id.id, 0.0)

                    if qty_avail <= 0.0:
                        # there will be nothing to consume for this raw material
                        continue

                    raw_product = [move for move in production.move_lines]
                    if raw_product:
                        for consume_line in raw_product:
                            consume_line.action_consume(consume_line.product_qty, consume_line.location_id.id, context=context)

                    raw_product = [move for move in production.move_lines if move.product_id.id==scheduled.product_id.id]
                    if raw_product:
                        # qtys we have to consume
                        qty = total_consume - consumed_data.get(scheduled.product_id.id, 0.0)
                        #if float_compare(qty, qty_avail, precision_rounding=scheduled.product_id.uom_id.rounding) == 1:
                            # if qtys we have to consume is more than qtys available to consume
                        #    prod_name = scheduled.product_id.name_get()[0][1]
                        #    raise osv.except_osv(_('Warning!'), _('You are going to consume total %s quantities of "%s".\nBut you can only consume up to total %s quantities.') % (qty, prod_name, qty_avail))
                        #if qty <= 0.0:
                            # we already have more qtys consumed than we need
                        #    continue

                        consumed = 0
                        rounding = raw_product[0].product_uom.rounding

                        # sort the list by quantity, to consume smaller quantities first and avoid splitting if possible
                        raw_product.sort(key=attrgetter('product_qty'))

                        # search for exact quantity
                        for consume_line in raw_product:
                            if tools.float_compare(consume_line.product_qty, qty, precision_rounding=rounding) == 0:
                                # consume this line

                                consume_line.action_consume(qty, consume_line.location_id.id, context=context)
                                consumed = qty
                                break

                        index = 0
                        # consume the smallest quantity while we have not consumed enough
                        while tools.float_compare(consumed, qty, precision_rounding=rounding) == -1 and index < len(raw_product):
                            consume_line = raw_product[index]
                            to_consume = min(consume_line.product_qty, qty - consumed)
                            consume_line.action_consume(to_consume, consume_line.location_id.id, context=context)
                            consumed += to_consume
                            index += 1

        if not flag:
            if production_mode == 'consume_produce':
                # To produce remaining qty of final product
                #vals = {'state':'confirmed'}
                #final_product_todo = [x.id for x in production.move_created_ids]
                #stock_mov_obj.write(cr, uid, final_product_todo, vals)
                #stock_mov_obj.action_confirm(cr, uid, final_product_todo, context)
                produced_products = {}
                for produced_product in production.move_created_ids2:
                    if produced_product.scrapped:
                        continue
                    if not produced_products.get(produced_product.product_id.id, False):
                        produced_products[produced_product.product_id.id] = 0
                    produced_products[produced_product.product_id.id] += produced_product.product_qty

                for produce_product in production.move_created_ids:
                    produced_qty = produced_products.get(produce_product.product_id.id, 0)
                    subproduct_factor = self._get_subproduct_factor(cr, uid, production.id, produce_product.id, context=context)
                    rest_qty = (subproduct_factor * production.product_qty) - produced_qty

                    if rest_qty < production_qty:
                        prod_name = produce_product.product_id.name_get()[0][1]
                        raise osv.except_osv(_('Warning!'), _('You are going to produce total %s quantities of "%s".\nBut you can only produce up to total %s quantities.') % (production_qty, prod_name, rest_qty))
                    if rest_qty > 0 :
                        stock_mov_obj.action_consume(cr, uid, [produce_product.id], (subproduct_factor * production_qty), context=context)
                wf_service.trg_validate(uid, 'mrp.production', production_id, 'button_finished_validated', cr)
        if flag == 'consume':
            for raw_product in production.move_lines2:
                new_parent_ids = []
                parent_move_ids = [x.id for x in raw_product.move_history_ids]
                for final_product in production.move_created_ids2:
                    if final_product.id not in parent_move_ids:
                        new_parent_ids.append(final_product.id)
                for new_parent_id in new_parent_ids:
                    stock_mov_obj.write(cr, uid, [raw_product.id], {'move_history_ids': [(4,new_parent_id)]})


        return True

    def action_finished(self, cr, uid, ids, context=None):
        for production in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, production.id, {'date_finished': time.strftime('%Y-%m-%d %H:%M:%S'), 'state': 'finished'})
        return True

    def action_validated(self, cr, uid, ids, context=None):
        for production in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, production.id, {'state': 'validated'})
        return True

    def action_close(self, cr, uid, ids, context=None):
        for production in self.browse(cr, uid, ids, context=context):
            self.action_produce(cr, uid, production.id, production.product_qty, 'consume_produce', 'consume', context=context)
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
        """
        Se puede dar el caso de querer cancelar un producción en estado 'confirmed', la cuál no nos va a dejar si tenemos pickings en estado 
        distinto a 'draft' o 'cancel'. Lo que se hace para eso es cancelar el picking primero y aquí es cuando surge el problema. El botón cancelar cuando
        la producción es 'confirmed' llama directamente a esta función, pero cuando se cancela el picking el botón cancelar dispara el flujo hacia el estado 'cancel'
        (lo que pasa es que se ha cambiado el estado de la producción a 'picking_except')
        Si en otro instancia del navegador tenemos cargada la vista con el botón de cuando el estado de la producción aun era 'confirmed' y lo pulsamos
        no estamos moviendo el flujo y por tanto el flujo se queda descoordinado y provoca que el procurement_order se quede en 'running' siempre
        """
        if context is None:
            context = {}

        res = super(mrp_production, self).action_cancel(cr, uid, ids, context=context)
        
        if res:
            workflow = netsvc.LocalService("workflow")
            for production in self.browse(cr, uid, ids, context=context):
                if production.state == 'cancel':
                    workflow.trg_validate(uid, 'mrp.production', production.id, 'button_cancel', cr)

        return res

mrp_production()


