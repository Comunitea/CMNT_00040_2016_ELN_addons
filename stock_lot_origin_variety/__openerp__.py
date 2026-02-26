# -*- coding: utf-8 -*-
# Copyright 2026 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Lot Origin and Variety",
    "version": '8.0.1.0.1',
    "category": 'Warehouse Management',
    "description": """Add Origin and Variety to Lot/Serial numbers""",
    "author": 'Pedro Gómez',
    "website": 'www.elnogal.com',
    "depends": [
        'stock',
     ],
    "init_xml": [],
    "data": [
        'views/stock_production_lot_view.xml',
    ],
    "demo_xml": [],
    "installable": True
}
