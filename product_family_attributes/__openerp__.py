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

{
    "name" : "Product fields for product OpenERP module",
    "description": """
        With this module you can adds fields to OpenERP products.
        """,
    "version" : "1.0",
    "author" : "Pexego",
    "depends" : ["base", "product","stock", "purchase"],
    "category" : "Stock",
    "init_xml" : [],
    "update_xml" : [ "data/product_fields_data.xml",
                    "product_fields_view.xml",
                    "product_view.xml",
                    'security/ir.model.access.csv',
                    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}