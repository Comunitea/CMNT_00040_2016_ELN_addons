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
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

def rounding(f, r):
    if not r:
        return f
    return round(f / r) * r

class product_costs_line(osv.osv_memory):
    _name = 'product.costs.line'
    _description = ''
    _columns = {
        'sequence': fields.integer('Sequence', required=True),
        'name': fields.char('Name', size=255, required=True),
        'theoric_cost': fields.float('Theoric Cost', digits=(16,6), required=True),
        'theoric_cost_standard': fields.float('Theoric Cost Standard', digits=(16,6), required=True),
        'tcs_tc_percent': fields.float('TCS vs TC (%)', digits=(4,2), readonly="True"),
        'real_cost': fields.float('Real Cost', digits=(16,6), required=True),
        'tc_rc_percent': fields.float('TC vs RC (%)', digits=(4,2), readonly="True"),
        'tcs_rc_percent': fields.float('TCS vs RC (%)', digits=(4,2), readonly="True"),
        'inventory': fields.boolean('Inventory'),
        'total': fields.boolean('Total')
    }
    _defaults = {
        'theoric_cost': 0.0,
        'real_cost': 0.0
    }
    #_order = 'sequence asc, id asc'

    def _get_costs(self, cr, uid, ids, element=False, product_id=False, context=None):

        theoric = 0.0
        theoric_standard = 0.0
        real = 0.0
        element_facade = self.pool.get('cost.structure.elements')
        product_facade = self.pool.get('product.product')
        user_facade = self.pool.get('res.users')
        loc_facade = self.pool.get('stock.location')
        uom_obj = self.pool.get('product.uom')
        bom_obj = self.pool.get('mrp.bom')
        budline_facade = self.pool.get('budget.line')
        buditem_facade = self.pool.get('budget.item')
        sale_forecast = self.pool.get('sales.forecast')
        sale_forecast_line = self.pool.get('sales.forecast.line')
        if element and product_id:
            ele = element_facade.browse(cr, uid, element)
            product = product_facade.browse(cr, uid, product_id)
            # Time
            time_start = False
            time_stop = False
            if ele.time == 'current_year':
                year = time.strftime('%Y')
                time_start = "01-01-" + year + " 00:00:01"
                first_day, last_day = calendar.monthrange(int(year), 12)
                time_stop = str(last_day) + "-12-" + year + " 23:59:59"
            #elif ele.time == 'last_twelve_months':
            #    time_stop = time.strftime('%Y-%m-%d %H:%M:%S')
            #    start = datetime.date.today() + \
            #             relativedelta(months=-12)
            #    time_start = start.strftime("%Y-%m-%d") + " 00:00:01"
            # THEORIC COST
            if ele.cost_type == 'bom':
                #Valores en función de la lista de mateirales.
                # La recorremos (aquí en principio no iteramos)
                if product.route_ids[0].name == 'Manufacture' and product.bom_ids:
                #if product.supply_method == 'produce' and product.bom_ids:
                    bom = product.bom_ids[0] #Cogemos la primera
                    #aqui no hace falta iterar.
                    factor = uom_obj._compute_qty(cr, uid, bom.product_uom.id, bom.product_qty, product.uom_id.id)
                    res1, res2 = bom_obj._bom_explode(cr, uid, bom, product.id, factor / bom.product_qty, properties=[])#, addthis=False, level=0, routing_id=False)
                    if res1:
                        for r in res1:
                            productb = product_facade.browse(cr, uid, r['product_id'])
                            if productb:
                                theoric += productb.standard_price * r['product_qty']
                                theoric_standard += productb.standard_price_standard * r['product_qty']
                        theoric = theoric / (factor or 1.0)
                        theoric_standard = theoric_standard / (factor or 1.0)
            elif ele.cost_type == 'standard_price':
                    theoric = product.standard_price or 0.0
                    theoric_standard = product.standard_price_standard or 0.0
            elif ele.cost_type == 'ratio':
                if ele.distribution_mode == 'eur':
                    theoric = ele.cost_ratio * product.standard_price
                    theoric_standard = theoric
                elif ele.distribution_mode == 'units':
                    theoric = ele.cost_ratio
                    theoric_standard = theoric
                elif ele.distribution_mode == 'kg':
                    theoric = ele.cost_ratio * product.weight_net
                    theoric_standard = theoric
                elif ele.distribution_mode == 'min':
                    if product.route_ids[0].name == 'Manufacture' and product.bom_ids:
                        bom = product.bom_ids[0]
                        if bom.routing_id:
                            hours = 0.0
                            for wc_use in bom.routing_id.workcenter_lines:
                                wc = wc_use.workcenter_id
                                qty_per_cycle = uom_obj._compute_qty(cr, uid, wc_use.uom_id.id, wc_use.qty_per_cycle, product.uom_id.id)
                                hours += float((wc_use.hour_nbr / qty_per_cycle)  * (wc.time_efficiency or 1.0))
                            theoric = ele.cost_ratio * hours * 60
                            theoric_standard = theoric
            elif ele.cost_type == 'total':
                theoric = 0.0
                theoric_standard = 0.0
            elif ele.cost_type == 'inventory':
                theoric = 0.0
                theoric_standard = 0.0
            # REAL COST
            cost = 0.0
            context.update({'to_date': time_stop[:10]})
            obj_product = product_facade.browse(cr,
                                                uid,
                                                product_id,
                                                context=context)
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
            query = "select sum(price_unit)/sum(product_qty) from stock_move \
                        where product_id = " + str(product_id) + \
                        " and company_id = " + str(company.id) + \
                        " and location_dest_id in " + \
                        str(tuple(loc_dest_ids)) + \
                        " and state = 'done' \
                        and date <= '" + time_stop + \
                        "' and date >= '" + time_start + "'"
            cr.execute (query)
            a = cr.fetchall()
            if a and a[0] and a[0][0]:
                cost += a[0][0]
            real = cost
            print u"Costes para %s\n>> Teorico: %s Teorico Standard %s Real %s"%(product.name, theoric, theoric_standard, real)
        return theoric, theoric_standard, real

    def get_product_costs(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        prod = self.pool.get('product.product')
        prod_cost = self.pool.get('product.cost')
        prod_cost_line = self.pool.get('product.cost.lines')
        lines = []
        value = {}
        
        if context.get('product_id', False):
            pro = [context['product_id']]
        else:
            pro = prod.search(cr, uid, [])
            
        for product in prod.browse(cr, uid, pro):

            if product.cost_structure_id and product.cost_structure_id.elements:
                print u"Estructura de costes para %s >> %s"%(product.name, product.cost_structure_id.name)
                new_prod_cost_id = prod_cost.create(cr, uid, {'product_id': product.id, 
                                                              'date': time.strftime('%Y-%m-%d %H:%M:%S'), 
                                                              'company_id': product.cost_structure_id.company_id.id})
                el = product.cost_structure_id.elements
                sumtheo = 0.0
                sumtheostd = 0.0
                sumreal = 0.0
                theoric = 0.0
                theoric_standard = 0.0
                real = 0.0
                standard_price_standard = 0.0
                dock_cost_standard = 0.0
                
                for element in el:
                    if element.cost_type not in ('total', 'inventory'):
                        theoric, theoric_standard, real = self._get_costs(cr, uid, ids, element.id, product.id, context)
                        sumtheo += theoric
                        sumtheostd += theoric_standard
                        sumreal += real
                    else:
                        theoric = sumtheo
                        theoric_standard = sumtheostd
                        real = sumreal

                    vals = {'sequence': element.sequence,
                            'name': element.cost_type_id.name,
                            'theoric_cost': theoric,
                            'theoric_cost_standard': theoric_standard,
                            'real_cost': real,
                            'inventory': (element.cost_type in ('inventory')),
                            'total': (element.cost_type in ('total', 'inventory'))
                            }
                    new_id = self.create(cr, uid, vals)
                    lines.append(new_id)

                    vals['product_cost_id'] = new_prod_cost_id
                    prod_cost_line.create(cr, uid, vals)
                    if element.cost_type in ('inventory'):
                        standard_price_standard = theoric_standard #El ultimo valor tipo inventario encontrado para actualizar el producto
                    if element.cost_type in ('total'):
                        dock_cost_standard = theoric_standard #El ultimo valor tipo total encontrado para actualizar el producto
                
                vals = {}
                if (standard_price_standard or dock_cost_standard) and context.get('update_costs', False):
                    if standard_price_standard:
                        vals['standard_price_standard'] = standard_price_standard
                    if dock_cost_standard:
                        vals['dock_cost_standard'] = dock_cost_standard       
                    print 'Updating product costs: ', product.code, vals
                    prod.write(cr, uid, product.id, vals)

        if not context.get('cron', False):
            value = {
                'domain': str([('id', 'in', lines)]),
                'view_type': 'tree',
                'view_mode': 'tree',
                'res_model': 'product.costs.line',
                'type': 'ir.actions.act_window',
                'nodestroy': True}
            
        return value
    
    def show_product_costs(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        prod_cost = self.pool.get('product.cost')
        prod_cost_lines = self.pool.get('product.cost.lines')
        lines_ids = []
        value = {}
        if context.get('product_id', False):
            cost_ids = prod_cost.search(cr, uid, [('product_id', '=', context['product_id'])], order="date desc")
            if cost_ids:
                lines = prod_cost_lines.search(cr, uid, [('product_cost_id', '=', cost_ids[0])], order="sequence asc")
                if lines:
                    lines = prod_cost_lines.browse(cr, uid, lines)
                    for l in lines:
                        vals = {'sequence': l.sequence,
                                'name': l.name,
                                'theoric_cost': l.theoric_cost,
                                'theoric_cost_standard': l.theoric_cost_standard,
                                'tcs_tc_percent': l.tcs_tc_percent,
                                'real_cost': l.real_cost,
                                'tc_rc_percent': l.tc_rc_percent,
                                'tcs_rc_percent': l.tcs_rc_percent,
                                'inventory': l.inventory,
                                'total': l.total
                                }
                        new_id = self.create(cr, uid, vals)
                        lines_ids.append(new_id)
                else:
                    raise osv.except_osv(_('Warning !'), _('Could not show costs. No cost lines were found for this product!'))
            else:
                raise osv.except_osv(_('Warning !'), _('Could not show costs. There are no costs associated with this product!'))
            
        value = {
            'domain': str([('id', 'in', lines_ids)]),
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'product.costs.line',
            'type': 'ir.actions.act_window',
            'nodestroy': True}
            
        return value


class update_product_costs(osv.osv_memory):
    _name = 'update.product.costs'

    def action_update_product_costs_wzd(self, cr, uid, ids, context=None):
        if context is None: context = {}
        c = context.copy()
        c['cron'] = True
        c['update_costs'] = True
        return self.pool.get('product.costs.line').get_product_costs(cr, uid, ids, c)


