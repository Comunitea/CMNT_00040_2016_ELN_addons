# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 Pexego Sistemas Informáticos All Rights Reserved
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
import calendar
import datetime
from dateutil.relativedelta import relativedelta
import decimal_precision as dp

class product_costs_line(osv.osv_memory):
    _name = 'product.costs.line'
    _description = ''
    _columns = {
        'sequence': fields.integer('Sequence', required=True),
        'name': fields.char('Name', size=255, required=True),
        'theoric_cost': fields.float('Theoric Cost', digits_compute=dp.get_precision('Purchase Price'), required=True),
        'real_cost': fields.float('Real Cost', digits_compute=dp.get_precision('Purchase Price'), required=True)
    }
    _defaults = {
        'theoric_cost': 0.00,
        'real_cost': 0.00
    }

    def _get_cost_raw_material(self, cr, uid, ids, product=False, flag=False, context=None):
        if context is None:
            context = {}

        prod = self.pool.get('product.product')
        bom_obj = self.pool.get('mrp.bom')
        uom_obj = self.pool.get('product.uom')
        theoric = 0.0

        def _get_bom_recursivity(line, factor):
            product = self.pool.get('product.product').browse(cr,
                                                                uid,
                                                                line['product_id'])
            boms = {}
            for d in product.bom_ids:
                if not d.bom_id:
                    bom = d

                    if bom.routing_id:
                        y, x  = self.pool.get('mrp.bom')._bom_explode(cr,
                                                                    uid,
                                                                    bom,
                                                                    factor / bom.product_qty,
                                                                    properties=[],
                                                                    addthis=False,
                                                                    level=0,
                                                                    routing_id=False)
                        boms = y

                        for l in y:

                            product = self.pool.get('product.product').browse(cr,
                                                                            uid,
                                                                            l['product_id'])
                            if product.supply_method == 'produce' and product.bom_ids:
                                for c in product.bom_ids:
                                    if not c.bom_id:
                                        bom = c

                                        factor = self.pool.get('product.uom')._compute_qty(cr,
                                                                                                uid,
                                                                                                product.uom_id.id,
                                                                                                l['product_qty'],
                                                                                                bom.product_uom.id)
                                        a = _get_bom_recursivity(l, factor)
                                        if a:
                                            boms += a
                                        break
                    break

            return boms

        if product.bom_ids:

            bom = product.bom_ids[0]

            factor = uom_obj._compute_qty(cr, uid,
                                        product.uom_id.id,
                                        1.0,
                                        bom.product_uom.id)
            res2, res1  = bom_obj._bom_explode(cr, uid, bom, factor / bom.product_qty, properties=[], addthis=False, level=0, routing_id=False)

            if res2:
                lines = res2
                for r in res2:
                    product = prod.browse(cr, uid, r['product_id'])
                    if product.bom_ids:
                        for h in product.bom_ids:
                            if not h.bom_id:
                                bom = h

                                factor = uom_obj._compute_qty(cr, uid,
                                                                product.uom_id.id,
                                                                r['product_qty'],
                                                                bom.product_uom.id)
                                res3 = _get_bom_recursivity(r, factor)
                                if res3:
                                    lines += res3
                        break

                for a in lines:
                    if flag:
                        theoric += round(prod.browse(cr, uid, a['product_id']).theoric_cost, 4) or 0.0
                    else:
                        theoric += round(prod.browse(cr, uid, a['product_id']).standard_price, 4) or 0.0


        return theoric

    def _get_cost_productino_min(self, cr, uid, ids, product=False, context=None):
        cost = 0.0
        prod = self.pool.get('product.product')
        bom_obj = self.pool.get('mrp.bom')
        uom_obj = self.pool.get('product.uom')
        def _get_bom_recursivity(line, factor):
                    product = self.pool.get('product.product').browse(cr,
                                                                    uid,
                                                                    line['product_id'])
                    boms = {}
                    for d in product.bom_ids:
                        if not d.bom_id:
                            bom = d

                            if bom.routing_id:
                                y, x  = self.pool.get('mrp.bom')._bom_explode(cr,
                                                                            uid,
                                                                            bom,
                                                                            factor / bom.product_qty,
                                                                            properties=[],
                                                                            addthis=False,
                                                                            level=0,
                                                                            routing_id=False)
                                boms = x

                                for l in y:

                                    product = self.pool.get('product.product').browse(cr,
                                                                                    uid,
                                                                                    l['product_id'])
                                    if product.supply_method == 'produce' and product.bom_ids:
                                        for c in product.bom_ids:
                                            if not c.bom_id:
                                                bom = c
                                                if bom.routing_id:
                                                    factor = self.pool.get('product.uom')._compute_qty(cr,
                                                                                                        uid,
                                                                                                        product.uom_id.id,
                                                                                                        l['product_qty'],
                                                                                                        bom.product_uom.id)
                                                    a = _get_bom_recursivity(l, factor)
                                                    if a:
                                                        boms += a
                                                break
                            break

                    return boms
        if product.supply_method == 'produce':
            if product.bom_ids:
                bom = product.bom_ids[0]
                if bom.routing_id:

                    factor = uom_obj._compute_qty(cr, uid,
                                                product.uom_id.id,
                                                1.0,
                                                bom.product_uom.id)
                    res2, res1  = bom_obj._bom_explode(cr, uid, bom, factor / bom.product_qty, properties=[], addthis=False, level=0, routing_id=False)

                    if res1:
                        lines = res1

                        for r in res2:
                            product = prod.browse(cr, uid, r['product_id'])
                            if product.supply_method == 'produce' and product.bom_ids:
                                for h in product.bom_ids:
                                    if not h.bom_id:
                                        bom = h

                                        if bom.routing_id:
                                            factor = uom_obj._compute_qty(cr, uid,
                                                                        product.uom_id.id,
                                                                        r['product_qty'],
                                                                        bom.product_uom.id)
                                            res3 = _get_bom_recursivity(r, factor)
                                            if res3:
                                                lines += res3
                                        break

                    for a in lines:
                        cost += a['hour']
        return cost

    def _get_cost_production(self, cr, uid, ids, element=False, product=False,
                   context=None):

        if context is None:
            context = {}

        prod = self.pool.get('product.product')
        bom_obj = self.pool.get('mrp.bom')
        uom_obj = self.pool.get('product.uom')
        theoric = 0.0
        cost = 0.0
        for item in element.budget_item:
            if item.budget_item_id.type_c == 'min':
                cost = self._get_cost_productino_min(cr, uid, ids, product, context)
                if cost > 0.0:
                    theoric += round(float(cost * item.total),4)
            if item.budget_item_id.type_c == 'units':
                theoric += item.total
        return theoric

    def _get_cost_internal_logistics(self, cr, uid, ids, element=False, product=False, context=None):
        if context is None:
            context = {}
        theoric = 0.0
        for item in element.budget_item:
            if item.budget_item_id.type_c == 'kg':
                theoric += round(float(product.weight_net * item.total),4)
        return theoric

    def _get_cost_external_logistics(self, cr, uid, ids, element=False, product=False, context=None):
        if context is None:
            context = {}
        theoric = 0.0
        for item in element.budget_item:
            if item.budget_item_id.type_c == 'kg':
                theoric +=  round(float(product.weight_net * item.total),4)
        return theoric

    def _get_cost_structure(self, cr, uid, ids, element=False, product=False, context=None):
        if context is None:
            context = {}
        theoric = 0.0
        for item in element.budget_item:
            if item.budget_item_id.type_c == 'euros':
                theoric +=  round(float(item.total),4)
        return theoric

    def _get_cost_commercial(self, cr, uid, ids, element=False, product=False, context=None):
        if context is None:
            context = {}
        theoric = 0.0
        for item in element.budget_item:
            theoric += round(float(item.total),4)
        return theoric

    def get_product_costs(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        prod = self.pool.get('product.product')
        prod_cost = self.pool.get('product.cost')
        prod_cost_line = self.pool.get('product.cost.lines')
        element_facade = self.pool.get('cost.structure.elements')

        user_facade = self.pool.get('res.users')
        loc_facade = self.pool.get('stock.location')
        uom_obj = self.pool.get('product.uom')
        bom_obj = self.pool.get('mrp.bom')
        budline_facade = self.pool.get('budget.line')
        buditem_facade = self.pool.get('budget.item')
        sale_forecast = self.pool.get('sales.forecast')
        sale_forecast_line = self.pool.get('sales.forecast.line')
        lines = []
        value = {}
        if context.get('product_id', False):
            pro = [context['product_id']]
        else:
            pro = prod.search(cr, uid, [])
        for product in prod.browse(cr, uid, pro):

            if product.cost_structure_id:

                c = prod_cost.create(cr, uid, {'product_id': product.id,
                                                   'date': time.strftime('%Y-%m-%d %H:%M:%S')})
                el = product.cost_structure_id.elements
                sumtheo =  0.0
                muelle = 0.0
                theoric = 0.0
                real = 0.0
                for element in el:
                    if element.calculate:
                        if element.type == 'raw_material':
                            theoric = self._get_cost_raw_material(cr, uid, ids, product, True, context)
                            sumtheo += theoric
                        if element.type == 'production' and element.budget_item:
                            theoric = self._get_cost_production(cr, uid, ids, element, product, context)
                            sumtheo += theoric
                        if element.type == 'internal_logistics' and element.budget_item:
                            theoric = self._get_cost_internal_logistics(cr, uid, ids, element, product, context)
                            sumtheo += theoric
                        if element.type == 'warehouse' and element.totalline:
                            theoric = sumtheo
                        if element.type == 'external_logistics' and element.budget_item:
                            theoric = self._get_cost_external_logistics(cr, uid, ids, element, product, context)
                            sumtheo += theoric
                        if element.type == 'structure' and element.budget_item: #TODO Función
                            theoric = self._get_cost_structure(cr, uid, ids, element, product, context)
                            sumtheo += theoric
                        if element.type == 'muelle' and element.totalline:
                            theoric = sumtheo
                        if element.type == 'commercial' and element.budget_item:
                            theoric = self._get_cost_commercial(cr, uid, ids, element, product, context) #TODO Función
                            sumtheo += theoric
                        if element.type == 'total' and element.totalline:
                            theoric = sumtheo

                        today = time.strftime('%d-%m-%Y %H:%M:%S')
                        # DATA FOR WHERE CLAUSE
                        # Destination location
                        domain = ['|',
                                 ('usage', '=', 'customer'),
                                 ('usage', '=', 'production')]
                        loc_dest_ids = loc_facade.search(cr,
                                                         uid,
                                                         domain)
                        # Company
                        company = user_facade.browse(cr, uid, uid).company_id
                        # QUERY
                        #~ cr.execute("select sum(product_qty) from stock_move \
                                    #~ where product_id=" + str(product.id) + \
                                    #~ " and company_id=" + str(company.id) + \
                                    #~ " and location_dest_id in " + \
                                    #~ str(tuple(loc_dest_ids)) + \
                                    #~ " and state='done' \
                                    #~ and date<='" + today + "'")
                        #~ a = cr.fetchall()
                        #~ if a and a[0] and a[0][0]:
                            #~ real = a[0][0]

                        vals = {'sequence': element.sequence,
                                'name': element.cost_type_id.name,
                                'theoric_cost': theoric,
                                'real_cost': product.standard_price}
                        new_id = self.create(cr, uid, vals)
                        lines.append(new_id)

                        vals['total'] = element.totalline
                        vals['product_cost'] = c
                        prod_cost_line.create(cr, uid, vals)

        if not context.get('cron', False):
            value = {
                'domain': str([('id', 'in', lines)]),
                'view_type': 'tree',
                'view_mode': 'tree',
                'res_model': 'product.costs.line',
                'type': 'ir.actions.act_window',
                'nodestroy': True}
        return value

product_costs_line()
