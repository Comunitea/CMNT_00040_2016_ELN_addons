# -*- coding: utf-8 -*-
# Copyright 2018 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Product Ranking",
    "description" : """Add ranking fields to product""",
    "summary": "Add ranking fields to product",
    "version": "8.0.1.0.0",
    "category": "Product",
    "website": "https://www.elnogal.com",
    "author": "Pedro Gómez",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        "product",
        "stock",
    ],
    "data": [
        'views/product_ranking_view.xml',
        'views/product_view.xml',
        'security/ir.model.access.csv',
    ],
}
