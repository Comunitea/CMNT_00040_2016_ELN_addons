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
from osv import osv, fields
import time
import calendar
import datetime
from dateutil.relativedelta import relativedelta

class product_costs_line(osv.osv_memory):
    _name = 'product.costs.line'
    _description = ''
    _columns = {
        'sequence': fields.integer('Sequence', required=True),
        'name': fields.char('Name', size=255, required=True),
        'theoric_cost': fields.float('Theoric Cost', required=True),
        'real_cost': fields.float('Real Cost', required=True)
    }
    _defaults = {
        'theoric_cost': 0.00,
        'real_cost': 0.00
    }
    def _get_costs(self, cr, uid, ids, element=False, product_id=False, context=None):
        theoric = 0.00
        real = 0.00
        element_facade = self.pool.get('cost.structure.elements')
        product_facade = self.pool.get('product.product')
        user_facade = self.pool.get('res.users')
        loc_facade = self.pool.get('stock.location')
        
        if element and product_id:
            ele = element_facade.browse(cr, uid, element)
            product = product_facade.browse(cr, uid, product_id)
            # THEORIC COST
            if ele.cost_theoric_type == 'none':
                if ele.field_theoric_cost == 'theoric_cost':
                    theoric += product.theoric_cost
                    c = context.copy()
                    today = time.strftime('%Y-%m-%d')
                    c.update({'to_date': today})
                    obj_product = product_facade.browse(cr, uid, product_id, context=c)
                    theoric = theoric * obj_product.qty_available
            # REAL COST
            
            if ele.cost_real_type == 'none':
                if ele.field_real_cost == 'pmp':
                    cost = 0.00
                    # DATA FOR WHERE CLAUSE
                    # Time
                    time_start = False
                    time_stop = False
                    if ele.time == 'current_year':
                        year = time.strftime('%Y')
                        time_start = "01-01-" + year + " 00:00:01"
                        first_day, last_day = calendar.monthrange(int(year), 12)
                        time_stop = str(last_day) + "-12-" + year + " 23:59:59"
#                    elif ele.time == 'last_twelve_months':
#                        time_stop = time.strftime('%Y-%m-%d %H:%M:%S')
#                        start = datetime.date.today() + \
#                                relativedelta(months=-12)
#                        time_start = start.strftime("%Y-%m-%d") + " 00:00:01"
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
                    cr.execute("select sum(product_qty) from stock_move \
                                where product_id=" + str(product_id) + \
                                " and company_id=" + str(company.id) + \
                                " and location_dest_id in " + str(tuple(loc_dest_ids)) + \
                                " and state='done' \
                                and date<='" + time_stop + \
                                "' and date>='" + time_start + "'")
                    a = cr.fetchall()
                    
                    if a:
                        cost += a[0][0]
                    context.update({'to_date': time_stop[:10]})
                    obj_product = product_facade.browse(cr, uid, product_id, context=context)
                    real = cost * obj_product.qty_available
        return theoric, real

    def get_product_costs(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        prod = self.pool.get('product.product')
        lines = []
        if context.get('product_id', False):
            product = prod.browse(cr, uid, context['product_id'])
            if product.categ_id and product.categ_id.cost_structure_id:
                if product.categ_id.cost_structure_id.elements:
                    el = product.categ_id.cost_structure_id.elements
                    for element in el:
                        theoric, real = self._get_costs(cr,
                                                        uid,
                                                        ids,
                                                        element.id,
                                                        product.id,
                                                        context)
                        new_id = self.create(cr,
                                             uid,
                                             {'sequence': element.sequence,
                                              'name': element.cost_type_id.name,
                                              'theoric_cost': theoric,
                                              'real_cost': real})
                        lines.append(new_id)
        value = {
            'domain': str([('id', 'in', [lines])]),
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'product.costs.line',
            'type': 'ir.actions.act_window',
            'nodestroy': True}
        return value

product_costs_line()
