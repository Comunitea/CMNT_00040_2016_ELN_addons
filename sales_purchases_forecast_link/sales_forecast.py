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
from odoo.osv import osv, fields
import time
from odoo.tools.translate import _

class sales_forecast(osv.osv):
    _inherit = 'sales.forecast'

    def generate_purchases_forecast(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        product_obj = self.pool.get('product.product')
        forecast_obj = self.pool.get('purchases.forecast')
        forecast_line_obj = self.pool.get('purchases.forecast.line')
        uom_obj = self.pool.get('product.uom')
        res = {}
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                  'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        forecast_lines = []
        forecasts = []
        name = ''
        year = 0
        user_company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id
        company_id = user_company_id and user_company_id.id or False
        new_id = False
        
        def _get_bom_recursivity(bom, factor):
            product_obj = self.pool.get('product.product')
            uom_obj = self.pool.get('product.uom')
            bom_obj = self.pool.get('mrp.bom')
            res = []
            res1, res2 = bom_obj._bom_explode(cr, uid, bom, bom.product_id, factor, properties=[])
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
                else: # Se compra
                    res.append(item)
            return res

        #necesitamos forecast_lines: contiene todas las lineas de las previsiones de ventas
        for cur in self.browse(cr, uid, ids):
            year = cur.year
            if cur.sales_forecast_lines:
                forecasts.append(cur.id)
                name += (name and ' - ') + cur.name
                for x in cur.sales_forecast_lines:
                    forecast_lines.append(x.id)
        if forecast_lines:
            new_id = forecast_obj.create(cr, uid, {'name': _('Purchase forecast. Origin: ') + name,
                                                   #'analytic_id': cur.analytic_id.id,
                                                   'commercial_id': uid,
                                                   'date': time.strftime('%d-%m-%Y'),
                                                   'company_id': company_id,
                                                   'state': 'draft',
                                                   'year': year
                                                    })
            for month in range(0, 12):
                for l in forecast_lines:
                    line = self.pool.get('sales.forecast.line').browse(cr, uid, l)
                    # Si producimos el producto, entonces debemos de entrar en la ldm para ver que necesitamos
                    # Si tiene lista de materiales y el producto no tiene proveedores asociados, interpretamos que se fabrica
                    # y en caso contrario suponemos que se compra
                    if line.product_id.bom_ids and not line.product_id.seller_ids: # Se fabrica
                        bom = line.product_id.bom_ids[0]
                        factor = uom_obj._compute_qty(cr, uid,
                                                    line.product_id.uom_id.id,
                                                    (eval('o.' + (months[month] + '_qty'), {'o': line})),
                                                    bom.product_uom.id)
                        factor = factor / bom.product_qty
                        lines = _get_bom_recursivity(bom, factor)
                        for x in lines:
                            if not res.get((x['product_id'], month)):
                                res[x['product_id'], month] = 0
                            res[x['product_id'], month] += x['product_qty']
                    else: # Se compra
                        if not res.get((line.product_id.id, month)):
                            res[line.product_id.id, month] = 0
                        res[line.product_id.id, month] += (eval('o.' + (months[month] + '_qty'), {'o': line}))
            if res:
                products = list(set([product[0] for product in res]))
                for product in products:
                    standard_price = product_obj.browse(cr, uid, product).standard_price
                    vals = {'purchases_forecast_id': new_id,
                            'actual_cost': standard_price,
                            'product_id': product}
                    for month in range(0, 12):
                        vals[months[month] + '_qty'] = res[product, month]
                        vals[months[month] + '_amount_total'] = res[product, month] * standard_price
                    forecast_line_obj.create(cr, uid, vals)
        return new_id

    def action_validate(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.generate_purchases_forecast(cr, uid, ids, context=context)

        return super(sales_forecast, self).action_validate(cr, uid, ids, context=context)

sales_forecast()
