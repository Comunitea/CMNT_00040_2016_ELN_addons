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
from osv import osv
from lxml import etree

class product_product(osv.osv):
    _inherit = "product.product"

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(product_product,self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
        if context is None:
            context = {}
        def _check_rec(eview, value, str_to_add):
            """busca recursivamente en el arch del xml el atributo domain con un valor dado y lo substituye por un nuevo valor"""
            if eview.attrib.get('name', False) == value:
                eview.addnext(etree.fromstring(str_to_add))
            for child in eview:
                res = _check_rec(child, value, str_to_add)
            return False

        if view_type == 'form':
            view_part_dimensions = u''
            view_part_features = u''
            view_part_packaging = u''
            field_names = []
            pfields = []
            sequences = {}
            product_field_ids = []
            product_fields = self.pool.get('product.fields').search(cr, uid, [])
            if product_fields:
                
                eview = etree.fromstring(res['arch'])
                for field in self.pool.get('product.fields').read(cr, uid, product_fields, ['field_id','sequence']):
                    pfields.append(field['field_id'][0])
                    sequences[str(field['field_id'][0])] = field['sequence']
                for pfield in pfields:
                    
                    product_field = self.pool.get('ir.model.fields').browse(cr, uid, pfield)
                    product_field_ids = self.pool.get('product.fields').search(cr, uid, [('sequence','=',int(sequences[str(pfield)]))])
                    if product_field_ids:
                        product_field_obj = self.pool.get('product.fields').browse(cr, uid, product_field_ids[0])
                        if str(product_field.name).startswith('x_') and product_field_obj.categ_id:
                            field_names.append(product_field.name)
                            if product_field_obj.group and product_field_obj.group== 'dimensions':
                                ids_dimensions = []
                                for x in product_field_obj.categ_id:
                                    ids_dimensions.append(x.id)
                                view_part_dimensions += u'<field name="%s"' % product_field.name
                                view_part_dimensions += u""" attrs="{'invisible':[('categ_id','not in',"""+str(ids_dimensions)+u""")]}" modifiers="{&quot;invisible&quot;: [[&quot;categ_id&quot;,  &quot;not in&quot;, """+str(ids_dimensions)+u"""]]}"/>\n"""
                                line = _check_rec(eview, 'dimensions', view_part_dimensions)
                                view_part_dimensions = ''
                            elif product_field_obj.group and product_field_obj.group== 'features':
                                ids_features = []
                                for x in product_field_obj.categ_id:
                                    ids_features.append(x.id)
                                view_part_features += u'<field name="%s"' % product_field.name
                                view_part_features += u""" attrs="{'invisible':[('categ_id','not in',"""+str(ids_features)+u""")]}" modifiers="{&quot;invisible&quot;: [[&quot;categ_id&quot;, &quot;!=&quot;, """+str(ids_features)+u"""]]}"/>\n"""
                                line = _check_rec(eview, 'features', view_part_features)
                                view_part_features = ''
                            elif product_field_obj.group and product_field_obj.group== 'packaging':
                                ids_packaging = []
                                for x in product_field_obj.categ_id:
                                    ids_packaging.append(x.id)
                                view_part_packaging += u'<field name="%s"' % product_field.name
                                view_part_packaging += u""" attrs="{'invisible':[('categ_id','not in',"""+str(ids_packaging)+u""")]}" modifiers="{&quot;invisible&quot;: [[&quot;categ_id&quot;, &quot;!=&quot;, """+str(ids_packaging)+u"""]]}"/>\n"""
                                line = _check_rec(eview, 'packaging2', view_part_packaging)
                                view_part_packaging = ''

                res['arch'] = etree.tostring(eview)
                res['fields'].update(self.fields_get(cr, uid, field_names, context))
                
                
        return res




product_product()