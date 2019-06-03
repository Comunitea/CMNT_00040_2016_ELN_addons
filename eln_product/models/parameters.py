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
from openerp import models, fields


class ProductParameters(models.Model):
    _name = 'product.parameter'

    name = fields.Char('Name', size=255, required=True, translate=True)
    type = fields.Selection([
        ('chemical', 'Chemical'),
        ('physical', 'Physical'),
        ('microbiological', 'Microbiological'),
        ('organoleptic','Organoleptic')
        ], string='Type', required=True)


class ProductParameterProduct(models.Model):
    _name = 'product.parameter.product'

    name = fields.Char('Name', size=64, required=True,
        default=lambda self: self.env['ir.sequence'].get('product.parameter.product') or '/')
    product_id = fields.Many2one('product.product', 'Product', ondelete='cascade')
    parameter_id = fields.Many2one('product.parameter', 'Parameter')
    value = fields.Char('Value', size=128, translate=True)

