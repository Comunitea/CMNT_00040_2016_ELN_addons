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
from osv import osv, fields

class stock_inventory_wzd(osv.osv_memory):
    _name = 'stock.inventory.wzd'
    _description = 'Print Stock in date filter by some fields'
    _columns = {
        'name':fields.char('name', size=64),
        'date': fields.datetime('Date', required=True),
        'company_id': fields.many2one('res.company','Company', required=True),
        'location_id': fields.many2one('stock.location', 'Parent location', required=True)
    }

    def print_report(self, cr, uid, ids, context=None):
        """prints report"""
        if context is None:
            context = {}
       
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids',[]),
             'model': 'stock.inventory.wzd',
             'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'stock.inventory.report',
            'datas': datas
            }

stock_inventory_wzd()
