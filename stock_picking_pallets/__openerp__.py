# -*- coding: utf-8 -*-
# Copyright 2023 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Pallets Control",
    "version": '8.0.1.0.1',
    "category": 'Warehouse Management',
    "description": """Stock Picking Pallets Control""",
    "author": 'Pedro Gómez',
    "website": 'www.elnogal.com',
    "depends": [
        'stock',
     ],
    "init_xml": [],
    "data": [
        'wizard/stock_transfer_details.xml',
        'views/stock_view.xml',
        'report/stock_picking_pallets_analysis_view.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
    "demo_xml": [],
    "installable": True
}
