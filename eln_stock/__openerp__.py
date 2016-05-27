# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
    'name': "El Nogal - Stock",
    'version': '1.0',
    'category': 'Warehouse Management',
    'description': """Stock module customizations for El Nogal""",
    'author': 'Pedro Gómez',
    'website': 'www.elnogal.com',
    "depends": ['base',
                'stock',
                'eln_sale',  # Because of commitment_date group
                'picking_invoice_rel',
                # 'stock_location',
                ],
    "init_xml": [],
    "data": [
        'stock_view.xml',
        'res_partner.xml',
        'wizard/postmigration_reconcile_quants_view.xml',
        'wizard/stock_picking_assign_multi.xml',
        'wizard/stock_picking_unreserve_multi.xml',
        'wizard/stock_picking_cancel_multi.xml',
    ],
    "demo_xml": [],
    "active": False,
    "installable": True
}
