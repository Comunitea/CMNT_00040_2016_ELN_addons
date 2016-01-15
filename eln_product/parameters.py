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

class product_parameters(osv.osv):
    _name = 'product.parameter'
    _columns = {
        'name': fields.char('Name', size=255, required=True, translate=True),
        'type': fields.selection([
            ('chemical', 'Chemical'),
            ('physical', 'Physical'),
            ('microbiological', 'Microbiological'),
            ('organoleptic','Organoleptic')], "Type", required=True)
    }
product_parameters()

class product_parameter_product(osv.osv):
    _name = 'product.parameter.product'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'product_id': fields.many2one('product.product', 'Product'),
        'parameter_id': fields.many2one('product.parameter', 'Parameter'),
        'value': fields.char('Value', size=128, translate=True)
    }
    _defaults = {
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'product.parameter.product') or '/',
    }
product_parameter_product()
