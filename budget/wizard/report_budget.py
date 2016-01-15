# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    Copyright (C) 2015- Comunitea Servicios Tecnologicos All Rights Reserved
#    $Kiko Sánchez$ <kiko@comunitea.com>
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

class report_budget(osv.osv_memory):
    _name = 'report.budget'
    _columns = {
        'version_id': fields.many2one('budget.version', 'Version', required=True),
        'item_id': fields.many2one('budget.item', 'Item'),
        'date_to': fields.date('Date to')
    }
    _defaults = {
        'date_to': lambda *a: time.strftime("%Y-%m-%d")
    }

    def print_report(self, cr, uid, ids,context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids',[]),
             'model': 'report.budget',
             'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report.budget.report.webkit',
            'datas': datas

        }


