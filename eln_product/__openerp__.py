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


{
    'name': "El Nogal Products",
    'version': '1.0',
    'category': '',
    'description': """Module that contents el nogal's product""",
    'author': 'Pexego Sistemas Informáticos',
    'website': 'www.pexego.es',
    "depends": [
        'base',
        'product',
        'product_extended',
        'mrp',
        'stock',
        'mail',
        'email_template',
        'hr',
    ],
    "init_xml": [],
    "data": [
        'security/ir.model.access.csv',
        'data/product_parameter_product_seq.xml',
        'data/product_revision_seq.xml',
        'data/product_sheet_shipments_seq.xml',
        'data/product_options_produc_seq.xml',
        'data/product_verifications_product.xml',
        'wizard/copy_product_ldm_view.xml',
        'wizard/send_datasheet_view.xml',
        'views/options_view.xml',
        'views/verifications_view.xml',
        'views/parameters_view.xml',
        'views/product_view.xml',
        'views/pricelist_view.xml',
    ],
    "demo_xml": [],
    "active": False,
    "installable": True
}
