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


class cost_structure(osv.osv):
    _name = 'cost.structure'
    _description = ''
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'elements': fields.one2many('cost.structure.element',
                                    'structure_id',
                                    'Elements',
                                    required=True),
        'year': fields.integer('Year', size=4, required=True),
        'budget_version_id': fields.many2one('budget.version', 'Version'),
        'company_id': fields.many2one('res.company', 'Company', required=True)

    }
    _defaults = {
        'name': '/',
    }
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}

        res = {}
        result = []
        result.append({'name': u"Coste Materia Prima",
                       'sequence': 1,
                       'type': 'raw_material'})
        result.append({'name': u"Coste Producción",
                       'sequence': 2,
                       'type': 'production'})
        result.append({'name': u"Coste Logística interna",
                       'sequence': 3,
                       'type': 'internal_logistics'})
        result.append({'name': u"Coste Almacén",
                       'sequence': 4,
                       'totalline': True,
                       'type': 'warehouse'})
        result.append({'name': u"Coste Logística Externa",
                       'sequence': 5,
                       'type': 'external_logistics'})
        result.append({'name': u"Coste Estructura",
                       'sequence': 6,
                       'type': 'structure'})
        result.append({'name': u"Coste Muelle",
                       'sequence': 7,
                       'totalline': True,
                       'type': 'muelle'})
        result.append({'name': u"Coste Comercial",
                       'sequence': 8,
                       'type': 'commercial'})
        #TODO Coste Punto Verde
        result.append({'name': u"Coste Final",
                       'sequence': 9,
                       'calculate': True,
                       'totalline': True,
                       'type': 'total'})

        res['elements'] = result
        return res

    def onchange_version_id(self, cr, uid, ids, budget_version_id, context=None):
        if context is None:
            context = {}
        if budget_version_id:
            version = self.pool.get('budget.version').browse(cr, uid, budget_version_id, context=context)
            return {'value': {'company_id': version.company_id.id}}
        return {}



cost_structure()


class cost_structure_element(osv.osv):
    _name = 'cost.structure.element'
    _description = ''
    #~ _rec_name="cost_type_id,structure_id"
    TYPES = [('raw_material', 'Raw material'),
             ('production', 'Production'),
             ('internal_logistics', 'Internal Logistics'),
             ('warehouse', 'Warehouse'),
             ('external_logistics', 'External Logistics'),
             ('structure','Structure'),
             ('muelle', 'Muelle'),
             ('commercial', 'Commercial'),
             ('total', 'Total')]
    _columns = {
        'name': fields.char('Name', size=255, required=True, readonly=True),
        'sequence': fields.integer('Sequence', required=True, readonly=True),
        'cost_type_id': fields.many2one('cost.type', 'Cost type', required=True),
        'structure_id': fields.many2one('cost.structure',
                                        'Structure',
                                        required=True),
        'budget_item': fields.many2many('budget.version.total2', 'element_version_total', 'version_id', 'element_id', 'Items'),
        'calculate': fields.boolean('Calculate'),
        'totalline': fields.boolean('Total'),
        'type': fields.selection(TYPES, 'type', required=True)
    }
    _defaults = {
        'name': '/',
        'sequence': 1,
    }


cost_structure_element()

