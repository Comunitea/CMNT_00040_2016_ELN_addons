# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos All Rights Reserved
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
#############################################################################
#from openerp.osv import osv, fields
from openerp.osv import osv, fields
from collections import deque

class maintenance_element(osv.osv):

    def _get_planta(self,cr ,uid, ids, field_name, args=None, context=None):
        result = {}
        elements = self.pool.get('maintenance.element').browse(cr, uid, ids, context)
        for element in elements:
            result[element.id]  = element.name
            elemento_aux = element
            while elemento_aux.padre_id:
                result[element.id] = elemento_aux.padre_id.name
                elemento_aux = elemento_aux.padre_id
        return result

    def _nombre_sin_planta(self, cr, uid, ids, name, args=None, context=None):
        result = {}
        elements = self.pool.get('maintenance.element').browse(cr, uid, ids, context)
        for element in elements:
            result[element.id] = ""
            if element.padre_id:
                arbol = deque()
                element_aux = element
                while element_aux.padre_id:
                    arbol.appendleft(element_aux)
                    element_aux = element_aux.padre_id
                for elemento in arbol:
                    result[element.id] += elemento.name + u"/"
                result[element.id]=result[element.id][:-1]
            else:
                result[element.id] = element.name
        return result

    def _complete_name(self, cr, uid, ids, name, args=None, context=None):
        res = {}
        for m in self.browse(cr, uid, ids, context=context):
            names = [m.name]
            parent = m.padre_id
            while parent:
                names.append(parent.name)
                parent = parent.padre_id
            res[m.id] = u' / '.join(reversed(names))
        return res

    _name = 'maintenance.element'
    _columns = {
            'name':fields.char('Name', size=60, required=True, readonly=False),
            'description': fields.text('Description'),
            'type':fields.selection([
                ('linea', 'Linea'),
                ('instalaciones', 'Instalaciones'),
                ('equipos', 'Equipo'),
                 ], 'Type', select=True),
            'padre_id':fields.many2one('maintenance.element', 'Father', required=False),
            'hijo_ids':fields.one2many('maintenance.element', 'padre_id', 'Hijos', required=False),
            'complete_name': fields.function(_complete_name, type='char', size=256, string="Complete name",
                            store={'maintenance.element': (lambda self, cr, uid, ids, c={}: ids, ['name', 'padre_id'], 10)}),
            'product_id':fields.many2one('product.product', 'product associated', required=False),
            'asset_id':fields.many2one('account.asset.asset', 'Active', required=False),
            'analytic_account_id':fields.many2one('account.analytic.account', 'Analytic account'),
            'analytic_journal_id':fields.many2one('account.analytic.journal', 'Analytic journal', required=True),
            'codigo':fields.char('Code', size=64, required=False, readonly=False),
            'maintenance_type_ids':fields.many2many('maintenance.type', 'maintenanceelement_maintenancetype_rel', 'element_id', 'type_id', 'Maintenance type'),
            'planta':fields.function(_get_planta, method=True, type='char', string='Floor', store=False),
            'nombre_sin_planta':fields.function(_nombre_sin_planta, method=True, type='char', string='Name without floor',
                                                  store = {
                                               'maintenance.element': (lambda self, cr, uid, ids, c={}: ids, ['name','padre_id'], 10),
                                               }),
            #'order_ids':fields.many2many('maintenance.element', 'maintenanceelement_workorder_rel', 'element_id', 'order_id', 'Work order', required=False),

                    }
maintenance_element()
