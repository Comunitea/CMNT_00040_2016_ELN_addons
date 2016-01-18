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

class planning_report_wizard(osv.osv_memory):
    _name = 'planning.report.wizard'
    
    _columns = {
        'name': fields.char('name', size=64),
        'route_id': fields.many2one('route', 'Route'),
        'date': fields.date('Date', required=True)
    }
    _defaults = {
        'name': lambda *a: 'planning_report', #será el nombre del archivo generado
    }
    def print_report(self, cr, uid, ids,context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids',[]),
             'model': 'planning.report.wizard',
             'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'planning_report',
            'datas': datas

        }

planning_report_wizard()

