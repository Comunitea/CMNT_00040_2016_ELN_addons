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
from openerp.osv import osv
import time
import calendar
class purchases_forecast(osv.osv):
    _inherit = 'purchases.forecast'

    def generate_master_procurement_schedule(self, cr, uid, ids, context=None):
        proc_obj = self.pool.get('stock.plannings')
        product_obj = self.pool.get('product.product')
        warehouse_obj = self.pool.get('stock.warehouse')
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                  'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        # periods = {month: {'id_producto': (prev, real)}}
        periods = {}

        for cur in self.browse(cr, uid, ids):
            if cur.purchases_forecast_lines:
                for month in range(0, 12):
                    year = cur.date[:4]
                    month = str(month)
                    periods[month] = {}
                    for line in cur.purchases_forecast_lines:
                        qty = 0.0

                        month_ = str(int(month) +1)

                        first_day, last_day = calendar.monthrange(int(time.strftime('%Y')),int(month_))
                        if len(month_) == 1:
                            complet_last_date = year+"-0"+month_+"-"+str(last_day)
                            complet_first_date = year+"-0"+month_+"-01"
                        else:
                            complet_last_date = year+"-"+month_+"-"+str(last_day)
                            complet_first_date = year+"-"+month_+"-01"

                        if periods[month].get(line.product_id.id, False):
                            periods[month][line.product_id.id][0] += eval('o.' + (months[int(month)] + '_qty'), {'o': line})
                        else:
                            periods[month][line.product_id.id] = []
                            purchases_lines = self.pool.get('purchase.order.line').search(cr, uid, [('product_id','=',line.product_id.id),('date_planned', '<=', complet_last_date), ('date_planned','>=', complet_first_date)])

                            if purchases_lines:
                                for pline in self.pool.get('purchase.order.line').browse(cr, uid, purchases_lines):
                                    qty += pline.product_qty

                            periods[month][line.product_id.id].append((eval('o.' + (months[int(month)] + '_qty'), {'o': line}), qty))

                if periods:
                    for period in periods:
                        # month: {'sale': {'id_producto': cantidad}, 'purchase': {'id_producto': cantidad}}
                        if period:
                            new_ids = []
                            warehouse = warehouse_obj.search(cr, uid, [('company_id','=', cur.company_id.id)])
                            if not warehouse:
                                raise osv.except_osv(_('Error'), _('It has not warehouse configured for this company! You must create one.'))
                            for product in periods[period]:
                                new_id = proc_obj.create(cr, uid, {
                                                                'product_id': product,
                                                                'to_procure': periods[period][product][0][0],
                                                                'planned_outgoing': periods[period][product][0][1],
                                                                'company_id': cur.company_id.id,
                                                                'period_id': str(period) ,
                                                                'warehouse_id': warehouse[0],
                                                                'product_uom': product_obj.browse(cr, uid, product).uom_id.id
                                                            })
                                new_ids.append(new_id)

        return True

    def action_validate(self, cr, uid, ids, context=None):

        res = super(purchases_forecast, self).action_validate(cr, uid, ids, context=context)

        self.generate_master_procurement_schedule(cr, uid, ids, context)
        return res

