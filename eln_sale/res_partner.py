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
from openerp.osv import osv, fields

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'product_ids': fields.one2many('partner.product', 'partner_id', 'Price list'),
        'property_product_pricelist_indirect_invoicing': fields.property(
            'product.pricelist',
            type='many2one', 
            relation='product.pricelist', 
            domain=[('type','=','sale')],
            string="Sale Pricelist (Indirect Invoicing)", 
            view_load=True,
            help="This pricelist will be used, instead of the default one, for indirect sales invoicing to the current partner"),
    }
    
res_partner()

class partner_product(osv.osv):
    _name = 'partner.product'
    _columns = {
        'name': fields.char('Product Code', size=32, required=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
    }
    
partner_product()


