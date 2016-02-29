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
import time
import re
from openerp.report import report_sxw
from openerp import _
import calendar
import datetime

class planning_report_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(planning_report_parser, self).__init__(cr, uid, name, context)
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        routes = []
        moves = []
        pickings = []
        route = False

        if data.get('form',{}) and data['form'].get('date', ''):
            date = datetime.datetime.strptime(data['form']['date'], '%Y-%m-%d').strftime('%Y-%m-%d')
            date_start = date + ' 00:00:00'
            date_stop = date + ' 23:59:59'
            if data['form'].get('route_id', False):
                pickings = self.pool.get('stock.picking').search(self.cr, self.uid, [('type','=','out'),
                                                                                     ('real_date','>=',date_start),('real_date','<=',date_stop),
                                                                                     ('route_id','=', data['form']['route_id'][0])])
            else:
                pickings = self.pool.get('stock.picking').search(self.cr, self.uid, [('type','=','out'),
                                                                                     ('real_date','>=',date_start),('real_date','<=',date_stop)])

        if pickings:
            for pick in self.pool.get('stock.picking').browse(self.cr, self.uid, pickings):
                if pick.route_id:
                    routes.append(pick.route_id)
                if pick.move_lines:
                    a = [x.id for x in pick.move_lines]
                    moves = moves + a
        objects = []
        if routes:
            routes = list(set(routes))
            for route in routes:
                route.code = route.code
                route.name = route.name
                route.carrier = route.carrier_id.name
                route.lines = self.get_move_lines(moves, route.id)
                objects.append(route)
        return super(planning_report_parser, self).set_context(objects, data, ids, report_type=report_type)


    def get_move_lines(self, moves, route):
        move_obj = self.pool.get('stock.move')
        self.cr.execute('''select distinct(s.product_id) from stock_move s inner join stock_picking p on p.id=s.picking_id where s.id in %s and p.route_id=''' + str(route) + '''''', (tuple(moves),)) #TODO picking_id
        products = self.cr.fetchall()
        lines = []
        if products:
            products = list(x[0] for x in products)
            for product in self.pool.get('product.product').browse(self.cr, self.uid, products):
                self.cr.execute('''select s.product_uom, sum(s.product_qty) from stock_move s inner join stock_picking p on p.id=s.picking_id
                                   where s.product_id = %s and s.id in ''' + str(tuple(moves)) + ''' and p.route_id=''' + str(route) + ''' group by s.product_uom''', (product.id,))

                move_lines = self.cr.fetchall()[0]

                product.code = product.default_code
                product.name = product.name
                product.qty = move_lines[1]
                product.uom = self.pool.get('product.uom').browse(self.cr, self.uid, move_lines[0]).name
                lines.append(product)

        return lines

report_sxw.report_sxw('report.planning_report', 'planning.report.wizard', 'eln_reports/report/planning_report_webkit.mako', parser=planning_report_parser, header=False)
