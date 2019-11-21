# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011-2017 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
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
from openerp.addons import jasper_reports
from . import stock_picking_out_report


def parser(cr, uid, ids, data, context):
    res = stock_picking_out_report.parser(cr, uid, ids, data, context)
    res['name'] = 'report.stock_picking_out_alt_2x'
    return res


jasper_reports.report_jasper('report.stock_picking_out_alt_2x', 'stock.picking', parser)
