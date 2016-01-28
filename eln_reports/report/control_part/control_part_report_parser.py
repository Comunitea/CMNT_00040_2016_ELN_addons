# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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


def parser( cr, uid, ids, data, context ):

    control_sheet_packing = False
    control_sheet_salted = False
    control_sheet_toasted = False
    control_sheet_fried = False
    control_sheet_mixed = False

    #import ipdb; ipdb.set_trace()

    for production in self.pool.get(cr.dbname).get('mrp.production').browse(cr, uid, ids):
        if production.routing_id and production.routing_id.workcenter_lines:
            for line in production.routing_id.workcenter_lines:                
                control_sheet_packing = control_sheet_packing or line.workcenter_id.control_sheet_packing
                control_sheet_salted = control_sheet_salted or line.workcenter_id.control_sheet_salted
                control_sheet_toasted = control_sheet_toasted or line.workcenter_id.control_sheet_toasted
                control_sheet_fried = control_sheet_fried or line.workcenter_id.control_sheet_fried
                control_sheet_mixed = control_sheet_mixed or line.workcenter_id.control_sheet_mixed
    
    parameters = {}
    ids = ids
    name = 'report.control_part'
    model = 'mrp.production'
    data_source = 'model'
    parameters['control_sheet_packing'] = control_sheet_packing
    parameters['control_sheet_salted'] = control_sheet_salted
    parameters['control_sheet_toasted'] = control_sheet_toasted
    parameters['control_sheet_fried'] = control_sheet_fried
    parameters['control_sheet_mixed'] = control_sheet_mixed
    return { 
        'ids': ids, 
        'name': name, 
        'model': model, 
        'records': [], 
        'data_source': data_source,
        'parameters': parameters,
    }
    
jasper_reports.report_jasper('report.control_part', 'mrp.production', parser)
