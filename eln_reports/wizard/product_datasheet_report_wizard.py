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
from tools.translate import _

def _lang_get(self, cr, uid, context=None):
    obj = self.pool.get('res.lang')
    ids = obj.search(cr, uid, [('translatable','=',True)])
    res = obj.read(cr, uid, ids, ['code', 'name'], context=context)
    res = [(r['code'], r['name']) for r in res]
    return res

class product_datasheet_report_wizard(osv.osv_memory):
    _name = "product.datasheet.report.wizard"
    #ponemos el _rec_name igual a uno de los columns pues no tiene uno predefinido que sea name
    #_rec_name = "language"

    _columns = {
        'name': fields.char('name', size=64),
        'language': fields.selection(_lang_get, 'Language', required=True)
    }
    _defaults = {
        'name': lambda *a: 'product_datasheet', #será el nombre del archivo generado
        'language': lambda *a: 'es_ES',
    }
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids',[]),
             'model': 'product.product',
             'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'product_datasheet',
            'datas': datas
            }
    
product_datasheet_report_wizard()
