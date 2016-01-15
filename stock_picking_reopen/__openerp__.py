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
    "name" : "Stock Picking Reopen",
    "version" : "1.0",
    "author" : "Pedro Gómez",
    "category": 'Warehouse Management',
    'complexity': "normal",
    "description": """
Allows reopen pickings
======================

This module allows to reopen pickings (set to Ready to Process).

The intention is to allow to correct errors or add missing info which becomes 
usually only visible after printing the picking.

If de picking type is "in" and the cost method is "average price", the price of the product will not be reverted, so
you can leave the incorrect value, or fix the price manually.

    """,
    'website': 'http://www.elnogal.com',
    "depends" : ["stock"],
    'init_xml': [],
    # 'update_xml': ['stock_view.xml',
    #                'security/stock_picking_reopen_security.xml',
    #                ],
    'demo_xml': [],
    'installable': True,
    'auto_install': False,
}
