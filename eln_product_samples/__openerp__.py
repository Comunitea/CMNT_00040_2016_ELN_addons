# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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

{
    "name" : "El Nogal - Product Samples Management",
    "version" : "1.0",
    "author" : "Pexego",
    "website" : "http://www.pexego.es",
    "category" : "Enterprise Specific Modules",
    "description": """Product Samples Management in Openerp""",
    "depends" : [
                'product',
                'sale',
                'stock',
                'nan_partner_risk',
                ],
    "init_xml" : [],
    "demo_xml" : [],
    "data" : [
                    'sale_order_view.xml',
                    'stock_warehouse_view.xml',
                    'product_product_view.xml',
                    ],
    "installable": True,
    'active': False
}
