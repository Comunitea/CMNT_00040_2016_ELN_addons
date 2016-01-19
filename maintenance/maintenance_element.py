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
from openerp.osv import orm, fields
from collections import deque
from openerp.tools.translate import _

class maintenance_element(orm.Model):

    def name_get(self, cr, uid, ids, context=None):
        if context is None: context = {}
        res = []
        for element in self.browse(cr, uid, ids, context):
            name = element.codigo + u" " + element.name
            res.append((element.id, name))
        return res

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=80):
        """allows search by code too"""
        if args is None: args=[]
        if context is None: context={}

        if name:
            ids = self.search(cr, user, [('codigo', '=', name)]+ args, limit=limit, context=context)
            if not len(ids):
                ids = self.search(cr, user, [('codigo', operator, name)]+ args, limit=limit, context=context)
                ids += self.search(cr, user, [('name', operator, name)]+ args, limit=limit, context=context)
                ids = list(set(ids))
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)

        result = self.name_get(cr, user, ids, context)
        return result

    def _get_planta(self,cr ,uid, ids, field_name, args=None, context=None):
        result = {}
        elements = self.pool.get('maintenance.element').browse(cr, uid, ids, context)
        for element in elements:
            result[element.id]  = element.name
            elemento_aux = element
            if elemento_aux.type == 'plant':
                plant = elemento_aux
            else:
                plant = False

            while elemento_aux.padre_id and not plant:
                elemento_aux = elemento_aux.padre_id
                if elemento_aux.type == 'plant':
                    plant = elemento_aux

            result[element.id] = plant and plant.name or ""
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
    _parent_store = True
    _parent_name = "padre_id"
    _order = 'parent_left'
    _columns = {
            'name':fields.char('Name', size=60, required=True, readonly=False),
            'description': fields.text('Description'),
            'type':fields.selection([
                ('plant', 'Plant'),
                ('block', 'Block'),
                ('system', 'System'),
                ('subsystem', 'Subsystem'),
                ('equipment', 'Equipment'),
                 ], 'Type', select=True),
            'padre_id':fields.many2one('maintenance.element', 'Father', required=False),
            'hijo_ids':fields.one2many('maintenance.element', 'padre_id', 'Hijos', required=False),
            'parent_left': fields.integer('Left Parent', select=True),
            'parent_right': fields.integer('Right Parent', select=True),
            'complete_name': fields.function(_complete_name, type='char', size=256, string="Complete name",
                            store={'maintenance.element': (lambda self, cr, uid, ids, c={}: ids, ['name', 'padre_id'], 10)}),
            'product_id':fields.many2one('product.template', 'product associated', required=False),
            'asset_id':fields.many2one('account.asset.asset', 'Active', required=False),
            'analytic_account_id':fields.many2one('account.analytic.account', 'Analytic account', required=True),
            'codigo':fields.char('Code', size=64, required=True),
            'maintenance_type_ids':fields.many2many('maintenance.type', 'maintenanceelement_maintenancetype_rel', 'element_id', 'type_id', 'Maintenance type'),
            'planta':fields.function(_get_planta, method=True, type='char', string='Floor', store=False),
            'nombre_sin_planta':fields.function(_nombre_sin_planta, method=True, type='char', string='Name without floor',
                                                  store = {
                                               'maintenance.element': (lambda self, cr, uid, ids, c={}: ids, ['name','padre_id'], 10),
                                               }),
            'order_ids':fields.many2many('work.order', 'maintenanceelement_work_order_rel', 'element_id', 'order_id', 'Work order', required=False),
            'product_ids': fields.many2many('product.template', 'maitenance_element_product_tmpl_rel', 'element_id', 'product_id', 'Associated products'),
            'active': fields.boolean('Active')
                    }

    _defaults = {
        'active': True
    }

    _sql_constraints = [
        ('codigo_uniq', 'unique (codigo)', 'The code of the Maintenance Element must be unique!')
    ]

    def create_intervention_request(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'maintenance', 'intervention_request_form_view')
        request_id = self.pool.get('intervention.request').create(cr, uid, {'element_ids': [(6,0,ids)]})
        return {
            'name':_("Intervention request"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'intervention.request',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': request_id
        }

    def unlink(self, cr, uid, ids, context=None):
        if context is None: Context = {}
        for element in self.browse(cr, uid, ids, context=context):
            if element.hijo_ids:
                raise orm.except_orm(_('Error !'),_("Cannot delete an element that contains another elements"))
            request_ids = self.pool.get('intervention.request').search(cr, uid, [('element_ids', 'in', [element.id])])
            if request_ids:
                raise orm.except_orm(_('Error !'),_("Cannot delete an element associated to intervention requests"))
            work_order_ids = self.pool.get('work.order').search(cr, uid, [('element_ids', 'in', [element.id])])
            if work_order_ids:
                raise orm.except_orm(_('Error !'),_("Cannot delete an element associated to work orders"))

        return super(maintenance_element, self).unlink(cr, uid, ids, context=context)
