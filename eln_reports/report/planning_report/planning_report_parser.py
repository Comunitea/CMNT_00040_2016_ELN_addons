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
        #De momento el informe será multicompañía, por eso no ponemos el nombre de la empresa
        #header_report_name = ' - '.join((_('Planning report'), company.name))
        header_report_name = _('Planning report')
        footer_date_time = self.formatLang(str(datetime.datetime.today()), date_time=True)
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
                ('--footer-right', ' '.join((_('Page'), '[page]', _('of'), '[topage]'))),
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

        routes_pool = self.saca_rutas(date_done, route_id)
        routes = []

        if group_by_route or route_id:
            if routes_pool:
                for route in routes_pool:
                    picks_pool = self.saca_picks(date_done, route[0])
                    products = self.saca_products(picks_pool)
                    route_obj = route[1] or 'Sin Ruta', products
                    routes.append(route_obj)
            else:
                raise osv.except_osv(_('Error!'),  _('Ruta no encontrada.'))
        else:
            picks_pool = self.saca_picks(date_done, 'all')
            products = self.saca_products(picks_pool)
            if products:
                route_obj = 'Todas las rutas', products
                routes.append(route_obj)
            else:
                raise osv.except_osv(_('Error!'),  _('No hay nada.'))

        date_obj = date_done.split()[0] if date_done else 'Sin Fecha', routes
        dates.append(date_obj)

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
        #sql_products = "select s.product_id, pp.default_code, pt.name, sum(s.product_qty), pum.name, sum(s.product_uos_qty), pus.name from stock_move s " \
        #               "inner join product_template pt on pt.id = s.product_id " \
        #               "inner join product_product pp on pp.id = s.product_id " \
        #               "inner join stock_picking p on p.id = s.picking_id " \
        #               "inner join product_uom pum on s.product_uom = pum.id " \
        #               "inner join product_uom pus on s.product_uos = pus.id " \
        #               "where p.id in (%s) " \
        #               "group by s.product_id, pum.name, pus.name, pp.default_code, pt.name " \
        #               "order by pp.default_code, s.product_id"%picks
        sql_products = "select s.product_id, sum(s.product_qty), s.product_uom, sum(s.product_uos_qty), s.product_uos from stock_move s " \
                       "inner join product_product pp on pp.id = s.product_id " \
                       "inner join stock_picking p on p.id = s.picking_id " \
                       "where p.id in (%s) " \
                       "group by s.product_id, s.product_uom, s.product_uos, pp.default_code " \
                       "order by pp.default_code, s.product_id"%picks

        self.cr.execute(sql_products)
        products = self.cr.fetchall()

        product_obj = self.pool.get('product.product')
        uom_obj = self.pool.get('product.uom')
        res = []

        for product in products:
            product = (product[0], #id
                       product_obj.browse(self.cr, 1, product[0], self.context).default_code, #default_code
                       #product_obj.browse(self.cr, 1, product[0], self.context).name, #name
                       product_obj.browse(self.cr, 1, product[0], self.context).partner_ref, #partner_ref
                       product[1], #product_qty
                       uom_obj.browse(self.cr, 1, product[2], self.context).name, #product_uom
                       product[3], #product_uos_qty
                       uom_obj.browse(self.cr, 1, product[4], self.context).name, #product_uos
                       )
            res.append(product)

        return res

    def saca_picks(self, date_done = False, route_id = False):

        str_date, str_route = self.set_filter(date_done, route_id)
        if not route_id:
            str_route = 'and p.route_id isnull '
        if route_id == 'all':
            str_route = ''
        sql_dates = "select id from stock_picking p where " \
            "%s" \
            "state in ('%s', '%s', '%s') %s and " \
            "picking_type_id in (select id from stock_picking_type where code = '%s') " \
            "group by 1 order by route_id desc"%(str_date, 'assigned', 'partially_available', 'confirmed', str_route, 'outgoing')
        print sql_dates
        self.cr.execute (sql_dates)
        picks = self.cr.fetchall()

        return picks

    def saca_rutas(self, date_done = False, route_id = False):
        str_date, str_route = self.set_filter(date_done, route_id)
        sql_dates = "select route_id, r.name from stock_picking p " \
                    "left join route r on p.route_id = r.id " \
                    "where %s " \
                    "state in ('%s', '%s', '%s') %s and " \
                    "picking_type_id in (select id from stock_picking_type where code = '%s') " \
                    "group by 1, 2 order by route_id asc"%(str_date, 'assigned', 'partially_available', 'confirmed', str_route, 'outgoing')

        self.cr.execute (sql_dates)
        routes = self.cr.fetchall()

        return routes

    def set_filter(self, date_done = False, route_id = False):

        if route_id:
            str_route = " and p.route_id=%s "%route_id
        else:
            str_route = ''

        if date_done:
            #si hay fecha tope
            str_date =  "(date_trunc('%s', date_done) <= '%s' or date_done isnull) and "%('day', date_done)
        else:
            str_date = ''

        return str_date, str_route


HeaderFooterTextWebKitParser(
    'report.planning_report',
    'planning.report.wizard',
    'eln_reports/report/planning_report_webkit.mako',
    parser=planning_report_parser)
