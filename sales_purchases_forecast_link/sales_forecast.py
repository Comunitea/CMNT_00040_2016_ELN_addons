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
from tools.translate import _

class sales_forecast(osv.osv):

    _inherit = 'sales.forecast'

    _columns = {
        'purchase_forecast_id': fields.many2one('purchases.forecast', 'Purchase forecast')
    }

    def _get_bom_recursivity(self, cr, uid, line, factor):

        product_obj = self.pool.get('product.product')
        uom_obj = self.pool.get('product.uom')
        bom_obj = self.pool.get('mrp.bom')

        product = product_obj.browse(cr,
                                    uid,
                                line['product_id'])
        boms = {}
        for d in product.bom_ids:
            if not d.bom_id:
                bom = d

                x, y  = bom_obj._bom_explode(cr,
                                            uid,
                                            bom,
                                            factor / bom.product_qty,
                                            properties=[],
                                            addthis=False,
                                            level=0,
                                            routing_id=False)
                boms = x

                for l in x:

                    product = product_obj.browse(cr,
                                                uid,
                                                l['product_id'])
                    if product.supply_method == 'produce' and product.bom_ids:
                         for c in product.bom_ids:
                            if not c.bom_id:
                                bom = c

                                factor = uom_obj._compute_qty(cr,
                                                            uid,
                                                            product.uom_id.id,
                                                            l['product_qty'],
                                                            bom.product_uom.id)
                                a = self._get_bom_recursivity(cr, uid, l, factor)
                                if a:
                                    boms += a

                                break
                break
        return boms

    def generate_purchases_forecast(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        bom_obj = self.pool.get('mrp.bom')
        product_obj = self.pool.get('product.product')
        forecast_obj = self.pool.get('purchases.forecast')
        forecast_line_obj = self.pool.get('purchases.forecast.line')
        uom_obj = self.pool.get('product.uom')
        res = {}
        good_lines = []
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug',
            'sep', 'oct', 'nov', 'dec']

        forecast_lines = []
        forecasts = []
        name = ''
        year = 0
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id and self.pool.get('res.users').browse(cr, uid, uid).company_id.id or False
        year = 0
        for cur in self.browse(cr, uid, ids):

            year = cur.year

            if cur.sales_forecast_lines:
                forecasts.append(cur.id)
                name += cur.name + " - "
                for x in cur.sales_forecast_lines:
                    forecast_lines.append(x.id)

        if forecast_lines:
            new_id = forecast_obj.create(cr, uid, {'name': _('Purchase forecast. Origin: ') + name,
                                                   #'analytic_id': cur.analytic_id.id,
                                                   'commercial_id': uid,
                                                   'date': time.strftime('%d-%m-%Y'),
                                                   'company_id': company,
                                                   'state': 'draft',
                                                   'year': year
                                                    })

            self.write(cr, uid, forecasts, {'purchase_forecast_id': new_id})
            for month in range(0,12):

                for l in forecast_lines:
                    line = self.pool.get('sales.forecast.line').browse(cr, uid, l)
                    if line.product_id.supply_method == 'produce':

                        if not line.product_id.bom_ids:
                            raise osv.except_osv(_('Error !'), _('The product "%s" has no LdM') % line.product_id.name)
                            break
                        else:

                            bom = line.product_id.bom_ids[0]
                            factor = uom_obj._compute_qty(cr, uid,
                                                        line.product_id.uom_id.id,
                                                        (eval('o.' + (months[month] + '_qty'),{'o': line})),
                                                         bom.product_uom.id)
                            res1, res2 = bom_obj._bom_explode(cr, uid, bom, factor / bom.product_qty, properties=[], addthis=False, level=0, routing_id=False)

                            if res1:
                                lines = res1
                                for r in res1:
                                    product = product_obj.browse(cr, uid, r['product_id'])
                                    if product.supply_method == 'produce' and product.bom_ids:
                                        for a in product.bom_ids:
                                            if not a.bom_id:
                                                bom =  a
                                                factor = uom_obj._compute_qty(cr, uid,
                                                                                    product.uom_id.id,
                                                                                    r['product_qty'],
                                                                                    bom.product_uom.id)

                                                res3 = self._get_bom_recursivity(cr, uid, r, factor)
                                                if res3:
                                                    lines += res3
                                                break

                            for visited in lines:
                                product = product_obj.browse(cr, uid, visited['product_id'])
                                if product.supply_method != 'produce':
                                    good_lines.append(visited)

                            for x in good_lines:

                                if res.get(x['product_id']):
                                    res[x['product_id']][0] +=  x['product_qty']

                                else:
                                    res[x['product_id']] = []
                                    res[x['product_id']].append(x['product_qty'])

                            lines = []
                            good_lines = []

                    elif line.product_id.supply_method == 'buy':
                        if res.get(line.product_id.id):
                            res[line.product_id.id][0] += (eval('o.' + (months[month] + '_qty'),{'o': line}))

                        else:
                            res[line.product_id.id] = []
                            res[line.product_id.id].append(((eval('o.' + (months[month] + '_qty'),{'o': line}))))


                if res:

                    for product in res:
                        cur_forecast = forecast_obj.browse(cr, uid, new_id)
                        l_products = forecast_line_obj.search(cr, uid,
                            [('product_id','=', product),
                            ('purchases_forecast_id', '=', cur_forecast.id)])

                        #If there are already lines created for the same product,
                        #update the quantities. Else, I create a new line
                        if l_products:
                            l = forecast_line_obj.browse(cr, uid, l_products[0])
                            if l.product_id.id == product:
                                forecast_line_obj.write(cr, uid, l.id,
                                    {months[month] + '_qty': ((res[product][0]) + \
                                    (eval('o.' + (months[month] + '_qty'),{'o': l}))),
                                    months[month] + '_amount_total': ((res[product][0]) + (eval('o.' + (months[month] + '_qty'),{'o': l}))) * \
                                    l.actual_cost
                                    })
                        else:
                            forecast_line_obj.create(cr, uid, {
                                'purchases_forecast_id': new_id,
                                'actual_cost': product_obj.browse(cr, uid, product).standard_price,
                                'product_id': product,
                                months[month] + '_qty': res[product][0],
                                months[month] + '_amount_total': res[product][0] * product_obj.browse(cr, uid, product).standard_price})

                    res = {}

        return new_id


    def action_validate(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = self.generate_purchases_forecast(cr, uid, ids, context=context)

        return super(sales_forecast, self).action_validate(cr,uid, ids, context=context)

sales_forecast()
