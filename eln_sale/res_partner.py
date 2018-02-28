# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
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

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    product_ids = fields.One2many('partner.product', 'partner_id', 'Price list')
    property_product_pricelist_indirect_invoicing = fields.Many2one(
        string='Sale Pricelist (Indirect Invoicing)',
        comodel_name='product.pricelist',
        domain="[('type','=','sale')]",
        company_dependent=True,
        help='This pricelist will be used, instead of the default one, for indirect sales invoicing to the current partner')


class PartnerProduct(models.Model):
    _name = 'partner.product'
    
    name = fields.Char('Product Code', size=32, required=True)
    product_id = fields.Many2one(string="Product", comodel_name='product.product', required=True)
    partner_id = fields.Many2one(string="Partner", comodel_name='res.partner', required=True)
