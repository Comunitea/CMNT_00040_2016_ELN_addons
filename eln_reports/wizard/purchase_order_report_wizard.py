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
from openerp.osv import osv,fields
import pooler
import time
from openerp.tools.translate import _

def _lang_get(self, cr, uid, context=None):
    obj = self.pool.get('res.lang')
    ids = obj.search(cr, uid, [('translatable','=',True)])
    res = obj.read(cr, uid, ids, ['code', 'name'], context=context)
    res = [(r['code'], r['name']) for r in res]
    return res

class purchase_order_report_wizard(osv.osv_memory):
    _name = "purchase.order.report.wizard"

    _columns = {
        'name': fields.char('name', size=64),
        'language': fields.selection(_lang_get, 'Language', required=True),
        'delivery_address': fields.boolean('Delivery Address'),
        'signed': fields.boolean('Signed')
    }
    _defaults = {
        'name': lambda *a: 'purchase_order', #será el nombre del archivo generado
        'delivery_address': lambda *a: True,
        'signed': lambda *a: True,
        'language': lambda *a: 'es_ES',
    }
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids',[]),
             'model': 'purchase.order',
             'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'purchase_order',
            'datas': datas
            }

purchase_order_report_wizard()
