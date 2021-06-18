# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Packing",
    "version": '8.0.1.0.1',
    "category": 'Warehouse Management',
    "description": """Stock Picking Packing""",
    "author": 'Pedro Gómez',
    "website": 'www.elnogal.com',
    "depends": [
        'stock',
        'product_expiry',
        'eln_product',
        'product_data_sheet',
     ],
    "init_xml": [],
    "data": [
        'wizard/stock_picking_modify_packing_view.xml',
        'security/ir.model.access.csv',
        'views/res_company_view.xml',
        'views/stock_view.xml',
        'views/gs1_128_report_layout.xml',
        'views/gs1_128_report_x1.xml',
        'views/gs1_128_report_x2.xml',
        'views/report.xml',
    ],
    "demo_xml": [],
    "installable": True
}
