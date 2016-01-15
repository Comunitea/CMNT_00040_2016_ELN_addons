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
from report import report_sxw
import time

class stock_inventory_report(report_sxw.rml_parse):
    _name = 'report.stock.inventory.report'
    def __init__(self, cr, uid, name, context):

        super(stock_inventory_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'get_date_text': self.get_date_text,
            'get_company_text': self.get_company_text,
            'get_warehouse_text': self.get_warehouse_text,
            'get_total_value':self.get_total_value

        })
        self.context = context
        self.total = 0.0


    def get_date_text(self, form):

        """
        Returns the date text used on the report.
        """
        return form['date']

    def get_company_text(self, form):

        """
        Returns the company text used on the report.
        """
        company_obj = self.pool.get('res.company')
        company = None
        company = company_obj.browse(self.cr, self.uid, form['company_id'][0])
        return company.name

    def get_warehouse_text(self, form):

        """
        Returns the warehouse text used on the report.
        """
        warehouse_obj = self.pool.get('stock.location')
        warehouse = None
        warehouse = warehouse_obj.browse(self.cr, self.uid, form['location_id'][0])
        return warehouse.name

    def get_total_value(self, form):
        return self.total

    def lines(self, form, ids={}):

        """
        Returns all the data needed for the report lines
        """

        if not ids:
            ids = self.ids


        res = {}
        # Get moves

        ids_products = self.pool.get('product.product').search(self.cr, self.uid, [])

        ids_locations = self.pool.get('stock.location').search(self.cr, self.uid, [('id','child_of', [form['location_id'][0]])])
        lines = []

        self.context.update({'to_date': form['date'], 'location': ids_locations, 'company_id': form['company_id'][0]})
        for product in ids_products:
            self.context['date'] = form['date']
            obj_product = self.pool.get('product.product').browse(self.cr, self.uid, product, context=self.context)
            qty = obj_product.qty_available
            if qty:
                pmp = obj_product.standard_price_date
                value = pmp * qty
                lines.append((obj_product.default_code, obj_product.name, qty, pmp, value))
                self.total += value
        res['x'] = lines
        result = []
        for x in res.values():
            for l in x:
                result.append(l)
        return result

report_sxw.report_sxw('report.stock.inventory.report', 'stock.inventory.wzd', 'stock_valued_date/report/stock_inventory_report.rml', parser=stock_inventory_report, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

