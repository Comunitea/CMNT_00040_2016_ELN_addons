# -*- coding: utf-8 -*-
# Copyright 2022 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Tags',
    'description': """Add tags to products""",
    'version': '8.0.1.0.1',
    'author': 'Pedro Gómez',
    'website': 'www.elnogal.com',
    'depends': [
        'base',
        'product',
    ],
    'category': 'Product',
    'init_xml': [],
    'data': [
        'security/ir.model.access.csv',
        'views/product_tags_view.xml',
        'views/product_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
