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
        #recorremos todas las lineas de la primera lista de materiales del producto
        for bom in product.bom_ids[0].bom_line_ids:
            if bom.product_qty == 0:
                qty = 0
            else:
                qty = factor/bom.product_qty
            boms, y  = bom_obj._bom_explode(cr,
                                        uid,
                                        bom,
                                        bom.product_id,
                                        qty,
                                        properties=[])
            #sacamos las necesidades de cada linea
            #en boms, y si ahora miramos si alguna linea tiene bom
            for bom_in_boms in boms:
                #recorremos las lineas y sacamos el producto
                product = product_obj.browse(cr,
                                            uid,
                                            bom_in_boms['product_id'])
                #miramos si tiene bom
                if product.route_ids[0].name == 'Manufacture' and product.bom_ids[0].bom_line_ids:
                    #si tienen bom ...
                     for c in product.bom_ids[0].bom_line_ids:
                        bom = c
                        factor = uom_obj._compute_qty(cr,
                                                    uid,
                                                    product.uom_id.id,
                                                    bom_in_boms['product_qty'],
                                                    bom.product_uom.id)
                        a = self._get_bom_recursivity(cr, uid, bom_in_boms, factor)
                        if a:
                            boms += a

                        break
                break
        return boms

    def generate_purchases_forecast(self, cr, uid, ids, context=None):
        print u"Generar Previsaion de Compra"
        import ipdb; ipdb.set_trace()
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
        #necesitamos forecast_lines: contiene todas las lineas de las previsiones de ventas
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
                    #si producimos el producto, entonces debemos de entrar en la ldm para ver que necesitamos
                    #supongo que o se compra, o se fabrica y que siempre tiene una de las dos
                    if line.product_id.route_ids[0].name == 'Manufacture':
                        if not line.product_id.bom_ids:
                            #todos los productos fabricados deben de tener su ldm
                            raise osv.except_osv(_('Error !'), _('The product "%s" has no LdM') % line.product_id.name)
                        else:
                            bom = line.product_id.bom_ids[0]
                            factor = uom_obj._compute_qty(cr, uid,
                                                        line.product_id.uom_id.id,
                                                        (eval('o.' + (months[month] + '_qty'),{'o': line})),
                                                         bom.product_uom.id)
                            res1, res2 = bom_obj._bom_explode(cr, uid, bom, line.product_id, factor / bom.product_qty, properties=[])
                            lines = res1
                            # if res1:
                            #     lines = res1
                            #     for r in res1:
                            #         product = product_obj.browse(cr, uid, r['product_id'])
                            #         factor = uom_obj._compute_qty(cr, uid, product.uom_id.id, r['product_qty'],bom.product_uom.id)
                            #         res3 = self._get_bom_recursivity(cr, uid, r, factor)
                            #         if res3:
                            #             lines += res3
                            # print u"BoM: %s para %s (%s) en mes %s"%(lines, line.product_id.name, line.product_id.route_ids[0].name, month)
                            for visited in lines:
                                product = product_obj.browse(cr, uid, visited['product_id'])
                                if product.route_ids[0].name == 'Buy':
                                    good_lines.append(visited)
                            for x in good_lines:

                                if res.get(x['product_id']):
                                    res[x['product_id']][0] +=  x['product_qty']

                                else:
                                    res[x['product_id']] = []
                                    res[x['product_id']].append(x['product_qty'])
                            lines = []
                            good_lines = []

                    elif line.product_id.route_ids[0].name == 'Buy':
                        if res.get(line.product_id.id):
                            res[line.product_id.id][0] += (eval('o.' + (months[month] + '_qty'),{'o': line}))

                        else:
                            res[line.product_id.id] = []
                            res[line.product_id.id].append(((eval('o.' + (months[month] + '_qty'),{'o': line}))))
                print u"deberemos de tener en res la prvision"
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
