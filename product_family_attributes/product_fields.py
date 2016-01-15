# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Marta Vázquez Rodríguez$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import osv, fields
from tools.translate import _

class product_fields(osv.osv):
    _name = "product.fields"
    _description = "Add fields to product.product"

    def _get_fields_type(self, cr, uid, context=None):
        cr.execute('select distinct ttype,ttype from ir_model_fields')
        field_types = cr.fetchall()
        field_types_copy = field_types

        for types in field_types_copy:
            if not hasattr(fields,types[0]):
                field_types.remove(types)

        return field_types

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'field_description': fields.char('Field Label', size=64, required=True, translate=True),
        'translate':fields.boolean('Translate'),
        'required':fields.boolean('Required'),
        'product_id': fields.many2many('product.product', 'product_product_fields_rel', 'product_field_id','product_id', 'Products'),
        'sequence': fields.char('Sequence', size=3, select=1, readonly=True),
        'field_id': fields.many2one('ir.model.fields', 'product_id'),
        'categ_id': fields.many2many('product.category', 'product_fields_product_category', 'product_field_id', 'category_id', 'Category'),
        'ttype': fields.selection(_get_fields_type, 'Field Type', size=64, required=True),
        'selection': fields.char('Selection Options',size=256, help="List of options for a selection field, "
            "specified as a Python expression defining a list of (key, label) pairs. "
            "For example: [('blue','Blue'),('yellow','Yellow')]"),
        'relation': fields.char('Object Relation', size=64,
            help="For relationship fields, the technical name of the target model"),
        'relation_field': fields.char('Relation Field', size=64,
            help="For one2many fields, the field on the target model that implement the opposite many2one relationship"),
        'group': fields.selection([('',''),
                ('dimensions','Dimensions'),
                ('features','Features'),
                ('packaging', 'Packaging')],string="Group")
    }
    _defaults = {
        'name':lambda * a:'x_',
    }

    def create(self, cr, uid, vals, context=None):
        model_id = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'product.product')])[0]

        if 'selection' in vals:
            selection = vals['selection']
        else:
            selection = ''

        if 'relation' in vals:
            relation = vals['relation']
        else:
            relation = ''

        if 'relation_field' in vals:
            relation_field = vals['relation_field']
        else:
            relation_field = ''
        field_vals = {
            'field_description': vals['field_description'],
            'model_id': model_id,
            'model': 'product.product',
            'name': vals['name'],
            'ttype': vals['ttype'],
            'translate': vals['translate'],
            'required': vals['required'],
            'selection': selection,
            'relation': relation,
            'relation_field': relation_field,
            'state': 'manual',
        }

        vals['field_id'] = self.pool.get('ir.model.fields').create(cr, uid, field_vals)

        sequence = self.pool.get('ir.sequence').get(cr, uid, 'product.fields')
        vals['sequence'] = sequence

        id = super(product_fields, self).create(cr, uid, vals, context)
        return id


    def unlink(self, cr, uid, ids, context=None):
        raise osv.except_osv(_('Warning !'), _('You can\'t delete this field'))


    def write(self, cr, uid, ids, vals, context=None):
        values = {}

        if 'group' in vals:
            values['group'] = vals['group']
        if 'categ_id' in vals:
            values['categ_id'] = vals['categ_id']
        if 'required' in vals:
            values['required'] = vals['required']
        if 'translate' in vals:
            values['translate'] = vals['translate']

        id = super(product_fields, self).write(cr, uid, ids, values, context)
        return id


product_fields()