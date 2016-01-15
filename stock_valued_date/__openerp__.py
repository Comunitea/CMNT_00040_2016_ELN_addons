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
    'name': "Stock valued date",
    'version': '1.0',
    'category': '',
    'description': """Gets the value of stock on a date.""",
    'author': 'Pexego Sistemas Informáticos',
    'website': 'www.pexego.es',
    'license': 'AGPL-3',
    "depends": ['base', 'stock', 'product', 'mrp', 'sale_order_dates'],
    "init_xml": [],
    "update_xml": [
                # 'stock_picking_view.xml',
                # 'weighted_average_price_view.xml',
                # 'data/weighted_average_price_seq.xml',
                # 'security/ir.model.access.csv',
                # 'wizard/stock_inventory_wzd.xml',
                # 'wizard/stock_partial_picking_view.xml',
                # 'stock_inventory_report.xml',
                # 'stock_inventory_wizard.xml',
                # 'stock_data.xml',

        ],
    "demo_xml" : [],
    "active": False,
    "installable": True
}
