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
from openerp.osv import osv
from .webkit_parser_header_fix import HeaderFooterTextWebKitParser
import calendar
import datetime
from openerp.report import common


class planning_report_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(planning_report_parser, self).__init__(cr, uid, name, context)
        self.context = context
        company = self.pool.get('res.users').browse(
            self.cr, uid, uid, context=context).company_id
        header_report_name = ' - '.join((_('Planning report'),
                                        company.name))
        footer_date_time = self.formatLang(
            str(datetime.datetime.today()), date_time=True)
        self.localcontext.update({
            'cr': cr,
            'uid': uid,
            'report_name': _('Planning report'),
            'additional_args': [
                ('--header-font-name', 'Helvetica'),
                ('--footer-font-name', 'Helvetica'),
                ('--header-font-size', '10'),
                ('--footer-font-size', '6'),
                ('--header-left', header_report_name),
                ('--header-spacing', '2'),
                ('--footer-left', footer_date_time),
                ('--footer-right',
                 ' '.join((_('Page'), '[page]', _('of'), '[topage]'))),
                ('--footer-line',),
            ],
        })
    def set_context(self, objects, data, ids, report_type=None):

        dates = []
        route_id = data ['form'].get('route_id', False)
        group_by_route = data['form'].get('group_by_route', False)
        if route_id:
            route_id = route_id[0]
        date_done = data ['form'].get('date', False)
        print route_id
        dates_pool = self.saca_dates(date_done, route_id)
        if dates_pool:
            for date_done_tuple in dates_pool:
                date_done = date_done_tuple[0] or False
                #sacamos todas las rutas de cada fecha

                routes_pool = self.saca_rutas(date_done, route_id)
                routes = []
                if group_by_route:
                    picks_pool = self.saca_picks(date_done, 'all')
                    products = self.saca_products(picks_pool)
                    if products:
                        route_obj = 'Todas las rutas', products
                        routes.append(route_obj)
                    else:
                        raise osv.except_osv(_('Error!'),  _('No hay nada.'))

                else:
                    if routes_pool:
                        for route in routes_pool:
                            picks_pool = self.saca_picks(date_done, route[0])
                            products = self.saca_products(picks_pool)
                            route_obj = route[1] or 'Sin Ruta', products
                            routes.append(route_obj)
                    else:
                        raise osv.except_osv(_('Error!'),  _('Ruta no encontrada.'))



                date_obj = date_done.split()[0] if date_done else 'Sin Fecha', routes
                dates.append(date_obj)

        else:
             raise osv.except_osv(_('Error!'),  _('Fecha no válida.'))
        object = dates

        self.localcontext['data'] = data
        self.localcontext['objects'] = object
        self.localcontext['digits_fmt'] = self.digits_fmt
        self.localcontext['get_digits'] = self.get_digits
        self.datas = data
        self.ids = ids
        self.objects = object
        if report_type:
            if report_type=='odt' :
                self.localcontext.update({'name_space' :common.odt_namespace})
            else:
                self.localcontext.update({'name_space' :common.sxw_namespace})
        return

    def saca_products (self, picks_ids):
        picks = ','.join([str(x[0]) for x in picks_ids])
        sql_products = "select s.product_id, pt.name, sum(s.product_qty), pum.name, sum(s.product_uos_qty), pus.name from stock_move s " \
                       "inner join product_template pt on pt.id = s.product_id " \
                       "inner join stock_picking p on p.id = s.picking_id " \
                       "inner join product_uom pum on s.product_uom = pum.id " \
                       "inner join product_uom pus on s.product_uos = pus.id " \
                        "where p.id in (%s) " \
                       "group by s.product_id, pum.name, pus.name, pt.name"%picks
        print sql_products
        self.cr.execute(sql_products)
        products = self.cr.fetchall()
        return products

    def saca_dates(self, date_done = False, route_id = False):
        str_date, str_route = self.set_filter(date_done, route_id)
        if date_done:
            date_find = datetime.datetime.strptime(date_done, '%Y-%m-%d').strftime('%Y-%m-%d') + ' 00:00:00'
            str_date =  "date_trunc('%s', date_done) = '%s' and "%('day', date_find)
        else:
            str_date = ""

        sql_dates = "select date_trunc('%s', date_done) as date_done from stock_picking p where " \
                    "%s state in ('%s', '%s') %s and " \
                    "picking_type_id in (select id from stock_picking_type where code = '%s') " \
                    "group by 1 order by date_done desc"%('day',str_date, 'assigned', 'partially_available', str_route, 'outgoing')
        self.cr.execute (sql_dates)
        dates = self.cr.fetchall()
        return dates

    def saca_picks(self, date_done = False, route_id = False):

        str_date, str_route = self.set_filter(date_done, route_id)
        if not route_id:
            str_route = 'and p.route_id isnull '
        if route_id == 'all':
            str_route = ''
        sql_dates = "select id from stock_picking p where " \
            "%s" \
            "state in ('%s', '%s') %s and " \
            "picking_type_id in (select id from stock_picking_type where code = '%s') " \
            "group by 1 order by route_id desc"%(str_date, 'assigned', 'partially_available', str_route, 'outgoing')
        print sql_dates
        self.cr.execute (sql_dates)
        picks = self.cr.fetchall()
        print picks
        return picks

    def saca_rutas(self, date_done = False, route_id = False):
        str_date, str_route = self.set_filter(date_done, route_id)
        sql_dates = "select route_id, r.name from stock_picking p " \
                    "left join route r on p.route_id = r.id " \
                    "where %s " \
                    "state in ('%s', '%s') %s and " \
                    "picking_type_id in (select id from stock_picking_type where code = '%s') " \
                    "group by 1, 2 order by route_id asc"%(str_date, 'assigned', 'partially_available', str_route, 'outgoing')
        print sql_dates
        self.cr.execute (sql_dates)
        routes = self.cr.fetchall()

        return routes

    def set_filter(self, date_done = False, route_id = False):

        if route_id:
            str_route = " and p.route_id=%s "%route_id
        else:
            str_route =  ''

        if date_done:
            #si ahy fechas
            str_date =  "date_trunc('%s', date_done) = '%s' and "%('day', date_done)
        else:
            str_date = 'date_done isnull and '

        return str_date, str_route






        # print sql_dates
        # print dates
        # import ipdb; ipdb.set_trace()
        # if dates:
        #     for date_done_tuple in dates:
        #         print date_done_tuple
        #
        #     for date_done_tuple in dates:
        #         # RECORRO LAS FECHAS Y BUSCO PICKS PARA ESE DÍA
        #         date_done = date_done_tuple[0] or False
        #         if date_done:
        #             date_find = datetime.datetime.strptime(data['form']['date'], '%Y-%m-%d').strftime('%Y-%m-%d') + ' 00:00:00'
        #             str_date =  "date_trunc('%s', date_done) = '%s' and "%('day', date_find)
        #         else:
        #             str_date = ''
        #         #date_trun = datetime.datetime.strptime(date_done, '%Y-%m-%d').strftime('%Y-%m-%d')
        #         #date_start = date_trun + ' 00:00:00'
        #         #date_stop = date_trun + ' 23:59:59'
        #         if date_done:
        #             sql_dates = "select id from stock_picking p where " \
        #                          "%s" \
        #                         "state in ('%s', '%s') %s and " \
        #                         "picking_type_id in (select id from stock_picking_type where code = '%s') " \
        #                         "group by 1 order by date_done desc"%('day',str_date, 'assigned', 'partially_available', str_route, 'outgoing')
        #
        #         else:
        #             sql_dates = "select id from stock_picking p where " \
        #                          "%s" \
        #                         "state in ('%s', '%s') %s and " \
        #                         "picking_type_id in (select id from stock_picking_type where code = '%s') " \
        #                         "group by 1 order by date_done desc"%(str_date, 'assigned', 'partially_available', str_route, 'outgoing')
        #
        #         self.cr.execute (sql_dates)
        #         picks_x_dates = self.cr.fetchall()
        #         print '----------------------------------------'
        #         print u"Fecha: %s"%date_done_tuple
        #         picks = list(x[0] for x in picks_x_dates)
        #         print u'Lista de (ids) picks'%picks
        #
        #         domain = [('id', 'in', picks)]
        #         routes_x_date = self.pool.get('stock.picking').browse(self.cr, self.uid, picks[0])
        #         routes_x_date.routes, routes_x_date.no_routes = self.get_date_routes(domain)#, data ['form'].get('route_id', False))
        #
        #         # object.date = date_done
        #         # object.routes =
        #         objects.append(routes_x_date)
        #         print objects
        #
        # return super(planning_report_parser, self).set_context(objects, data, ids, report_type=report_type)

    def get_date_routes(self, pick_ids, route_id = False):

        route = False
        routes = []
        moves = []
        moves_no_route = []
        pickings = self.pool.get('stock.picking').search(self.cr, self.uid, pick_ids)

        if pickings:
            for pick in self.pool.get('stock.picking').browse(self.cr, self.uid, pickings):

                print "Pick id: %s >> Ruta %s"%(pick.id, pick.route_id.name)

                if pick.route_id:
                    routes.append(pick.route_id)

                    if pick.move_lines:
                        a = [x.id for x in pick.move_lines]
                        moves = moves + a
                else:
                    if pick.move_lines:
                        a = [x.id for x in pick.move_lines]
                        moves_no_route = moves_no_route + a
        objects = []
        import ipdb; ipdb.set_trace()
        print routes
        if routes:
            routes = list(set(routes))
            for route in routes:
                route.code = route.code or '---'
                route.name = route.name or u'Sin Asignar'
                route.carrier = route.carrier_id.name
                route.lines = self.get_move_lines(moves, route.id)
                objects.append(route)


        # Si no hay royute_id, debemos buscar todos los movimientos de todas las rutas.
        import ipdb; ipdb.set_trace()
        if moves_no_route:
            moves_no_route_ = self.get_move_lines(moves_no_route)
            import ipdb; ipdb.set_trace()
        return objects, moves_no_route_





HeaderFooterTextWebKitParser(
    'report.planning_report',
    'planning.report.wizard',
    'eln_reports/report/planning_report_webkit.mako',
    parser=planning_report_parser)
