# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Delivery Routes",
    "version": '8.0.1.0.1',
    "category": 'Sale',
    "description": """Delivery routes""",
    "author": 'Pedro Gómez',
    "website": 'www.elnogal.com',
    "depends": [
        'sale',
        'stock',
        'eln_sale',
     ],
    "init_xml": [],
    "data": [
        'wizard/wiz_default_delivery_route.xml',
        'security/ir.model.access.csv',
        'views/delivery_route_view.xml',
        'views/res_partner_view.xml',
        'views/stock_view.xml',
    ],
    "demo_xml": [],
    "installable": True
}
