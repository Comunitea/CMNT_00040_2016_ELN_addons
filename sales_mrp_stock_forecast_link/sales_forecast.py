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
from openerp.tools.translate import _

class sales_forecast(osv.osv):
    _inherit = 'sales.forecast'

    def generate_stock_forecast(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        forecast_obj = self.pool.get('forecast.kg.sold')
        forecast_line_obj = self.pool.get('forecast.kg.sold.line')
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                  'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        name = ''
        lines = {}
        new_id = False
        for cur in self.browse(cr, uid, ids):
            if cur.sales_forecast_lines:
                name += (name and ' - ') + cur.name
                new_id = forecast_obj.create(cr, uid, {'name': _('Forecast of kg sold. Origin: ') + name,
                                                       'analytic_id': cur.analytic_id.id,
                                                       'commercial_id': cur.commercial_id.id,
                                                       'date': time.strftime('%d-%m-%Y'),
                                                       'company_id': cur.company_id.id,
                                                       'year': cur.year
                                     })
                for month in range(0, 12):
                    for line in cur.sales_forecast_lines:
                        if line.product_id.format_id:
                            if not lines.get((line.product_id.format_id.id, month)):
                                lines[line.product_id.format_id.id, month] = 0
                            lines[line.product_id.format_id.id, month] += (eval('o.' + (months[month] + '_qty'), {'o': line})) * line.product_id.weight_net
                        else:
                            if not lines.get(('undefined', month)):
                                lines['undefined', month] = 0
                            lines['undefined', month] += (eval('o.' + (months[month] + '_qty'), {'o': line})) * line.product_id.weight_net
                if lines:
                    formats = list(set([element[0] for element in lines]))
                    for element in formats:
                        vals = {'kgsold_forecast_id': new_id,
                                }
                        if element == 'undefined':
                            vals['notes'] = _('undefined')
                        else:
                            vals['format_id'] = element
                        for month in range(0, 12):
                            vals[months[month] + '_kg'] = lines[element, month]
                        forecast_line_obj.create(cr, uid, vals)
        return new_id

    def generate_mrp_forecast(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        forecast_obj = self.pool.get('mrp.forecast')
        forecast_line_obj = self.pool.get('mrp.forecast.line')
        uom_obj = self.pool.get('product.uom')
        res = {}
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                  'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        forecast_lines = []
        forecasts = []
        name = ''
        user_company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id
        company_id = user_company_id and user_company_id.id or False
        new_id = False
        
        def _get_bom_recursivity(bom, factor):
            product_obj = self.pool.get('product.product')
            uom_obj = self.pool.get('product.uom')
            bom_obj = self.pool.get('mrp.bom')
            res = []
            res1, res2 = bom_obj._bom_explode(cr, uid, bom, bom.product_id, factor, properties=[])
            res = res2
            for item in res1:
                product_id = product_obj.browse(cr, uid, item['product_id'])
                bom_id = product_id.bom_ids and product_id.bom_ids[0]
                if bom_id and not product_id.seller_ids: # Se fabrica
                    factor = uom_obj._compute_qty(cr, uid,
                                                item['product_uom'],
                                                item['product_qty'],
                                                bom_id.product_uom.id)
                    factor = factor / bom_id.product_qty
                    res += _get_bom_recursivity(bom_id, factor)
            return res
        
        for cur in self.browse(cr, uid, ids):
            year = cur.year
            if cur.sales_forecast_lines:
                forecasts.append(cur.id)
                name += (name and ' - ') + cur.name
                for x in cur.sales_forecast_lines:
                    forecast_lines.append(x.id)
        if forecast_lines:
            new_id = forecast_obj.create(cr, uid, {'name': _('Forecast of production hours. Origin: ') + name,
                                                   'date': time.strftime('%d-%m-%Y'),
                                                   'company_id': company_id,
                                                   'state': 'draft',
                                                   'year': year
                                                    })
            for month in range(0, 12):
                for l in forecast_lines:
                    line = self.pool.get('sales.forecast.line').browse(cr, uid, l)
                    if line.product_id.bom_ids and not line.product_id.seller_ids: # Se fabrica
                        bom = line.product_id.bom_ids[0]
                        if not bom.routing_id:
                            break
                        factor = uom_obj._compute_qty(cr, uid,
                                                    line.product_id.uom_id.id,
                                                    (eval('o.' + (months[month] + '_qty'), {'o': line})),
                                                    bom.product_uom.id)
                        factor = factor / bom.product_qty
                        lines = _get_bom_recursivity(bom, factor)
                        for x in lines:
                            if not res.get((x['workcenter_id'], month)):
                                res[x['workcenter_id'], month] = [0, 0]
                            res[x['workcenter_id'], month][0] += x['hour']
                            res[x['workcenter_id'], month][1] += 0 # En tiempo real ponemos 0. Se cubrirá a mano mes a mes.
            if res:
                workcenters = list(set([workcenter[0] for workcenter in res]))
                for workcenter in workcenters:
                    vals = {'mrp_forecast_id': new_id,
                            'workcenter_id': workcenter}
                    for month in range(0, 12):
                        vals[months[month] + '_hours'] = res[workcenter, month][0]
                        vals[months[month] + '_real_time'] = res[workcenter, month][1]
                    forecast_line_obj.create(cr, uid, vals)

        return new_id

    def action_validate(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.generate_stock_forecast(cr, uid, ids, context=context)
        self.generate_mrp_forecast(cr, uid, ids, context=context)
        
        return super(sales_forecast, self).action_validate(cr, uid, ids, context=context)

sales_forecast()