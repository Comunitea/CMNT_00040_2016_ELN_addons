# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Data Sheet",
    "version": '8.0.1.0.1',
    "category": 'Product',
    "description": """Product technical and logistic sheets""",
    "author": 'Pedro Gómez',
    "website": 'www.elnogal.com',
    "depends": [
        'base',
        'product',
        'mrp',
        'hr',
        'eln_product',
     ],
    "init_xml": [],
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/copy_product_ldm_view.xml',
        'views/parameters_view.xml',
        'views/product_view.xml',
        'views/product_logistic_sheet_view.xml',
        'views/product_technical_sheet_view.xml',
    ],
    "demo_xml": [],
    "installable": True
}
