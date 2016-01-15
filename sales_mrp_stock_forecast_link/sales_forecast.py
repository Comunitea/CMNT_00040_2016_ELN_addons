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
from osv import osv
import time

class sales_forecast(osv.osv):

    _inherit = 'sales.forecast'

    def generate_stock_forecast(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        forecast_obj = self.pool.get('forecast.kg.sold')
        forecast_line_obj = self.pool.get('forecast.kg.sold.line')
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug',
            'sep', 'oct', 'nov', 'dec']

        lines = {}
        for cur in self.browse(cr, uid, ids):
            if cur.sales_forecast_lines:
                new_id = forecast_obj.create(cr, uid, {'name': cur.name,
                                                   'analytic_id': cur.analytic_id.id,
                                                   'commercial_id': cur.commercial_id.id,
                                                   'date': time.strftime('%d-%m-%Y'),
                                                   'company_id': cur.company_id.id,

                                                   'year': cur.year

                                     })
                for month in range(0,12):

                    for line in cur.sales_forecast_lines:
                        if lines.get(line.product_id.format_id.id):
                            lines[line.product_id.format_id.id] += (eval('o.' + (months[month] + '_qty'),{'o': line})) * line.product_id.weight_net
                        elif lines.get('undefined'):
                            lines['undefined'] += (eval('o.' + (months[month] + '_qty'),{'o': line})) * line.product_id.weight_net
                        else:
                            if line.product_id.format_id:
                                lines[line.product_id.format_id.id] = (eval('o.' + (months[month] + '_qty'),{'o': line})) * line.product_id.weight_net
                            else:
                                lines['undefined'] = (eval('o.' + (months[month] + '_qty'),{'o': line})) * line.product_id.weight_net

                    if lines:
                        for format in lines:
                            cur_forecast = forecast_obj.browse(cr, uid, new_id)
                            l_formats = forecast_line_obj.search(cr, uid,
                                ['|',('format_id','=', format), ('notes','=', format),
                                ('kgsold_forecast_id', '=', cur_forecast.id)])
                            if l_formats:
                                l = forecast_line_obj.browse(cr, uid, l_formats[0])
                                forecast_line_obj.write(cr,
                                                        uid,
                                                        l.id,
                                                        {months[month] + '_kg': (eval('o.' + (months[month] + '_kg'),{'o': l})) + lines[format]})
                            else:
                                if format == 'undefined':
                                    forecast_line_obj.create(cr, uid, {
                                                        'kgsold_forecast_id': new_id,
                                                        months[month] + '_kg': lines[format],
                                                        'notes': 'undefined'
                                                        })
                                else:
                                    forecast_line_obj.create(cr, uid, {
                                                        'kgsold_forecast_id': new_id,
                                                        months[month] + '_kg': lines[format],
                                                        'format_id': format
                                                        })

                        lines = {}
        return new_id

    def generate_mrp_forecast(self, cr, uid, ids, context=None):

        if context is None:
            context = {}

        forecast_obj = self.pool.get('mrp.forecast')
        forecast_line_obj = self.pool.get('mrp.forecast.line')
        prod = self.pool.get('product.product')
        bom_obj = self.pool.get('mrp.bom')
        uom_obj = self.pool.get('product.uom')

        res = {}

        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul',
                'aug', 'sep', 'oct', 'nov', 'dec']
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
        for cur in self.browse(cr, uid, ids):
            if cur.sales_forecast_lines:
                new_id = forecast_obj.create(cr, uid, {'name': cur.name,
                                                   'date': time.strftime('%d-%m-%Y'),
                                                   'company_id': cur.company_id.id,

                                                   'year': cur.year
                                   })

                for month in range(0,12):

                    for line in cur.sales_forecast_lines:

                        if line.product_id.supply_method == 'produce':

                            if not line.product_id.bom_ids:
                                break
                            else:

                                bom = line.product_id.bom_ids[0]
                                if not bom.routing_id:
                                    break
                                else:
                                    factor = uom_obj._compute_qty(cr, uid,
                                                                line.product_id.uom_id.id,
                                                                (eval('o.' + (months[month] + '_qty'),{'o': line})),
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
                                        if res.get(a['workcenter_id']):
                                            res[a['workcenter_id']][0] += a['hour']
                                            res[a['workcenter_id']][1] += a['real_time']
                                        else:
                                            res[a['workcenter_id']] = []
                                            res[a['workcenter_id']].append(a['hour'])
                                            res[a['workcenter_id']].append(a['real_time'])
                    if res:
                        for workcenter in res:
                            cur_forecast = forecast_obj.browse(cr, uid, new_id)
                            l_workcenters = forecast_line_obj.search(cr, uid,
                                [('workcenter_id','=', workcenter),
                                ('mrp_forecast_id', '=', cur_forecast.id)])

                            #If there are already lines created for the same workcenter,
                            #update the quantities. Else, I create a new line
                            if l_workcenters:
                                l = forecast_line_obj.browse(cr, uid, l_workcenters[0])
                                if l.workcenter_id.id == workcenter:
                                    forecast_line_obj.write(cr, uid, l.id,
                                        {months[month] + '_hours': ((res[workcenter][0]) + \
                                        (eval('o.' + (months[month] + '_hours'),{'o': l}))),
                                        months[month] + '_real_time': ((res[workcenter][1]) + \
                                        (eval('o.' + (months[month] + '_real_time'),{'o': l})))
                                        })
                            else:
                                forecast_line_obj.create(cr, uid, {
                                    'mrp_forecast_id': new_id,
                                    'workcenter_id': workcenter,
                                    months[month] + '_hours': res[workcenter][0],
                                    months[month] + '_real_time': res[workcenter][1] })
                        res = {}

        return new_id



    def action_validate(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.generate_stock_forecast(cr, uid, ids, context=context)
        self.generate_mrp_forecast(cr, uid, ids, context=context)
        return super(sales_forecast, self).action_validate(cr,uid, ids, context=context)

sales_forecast()
