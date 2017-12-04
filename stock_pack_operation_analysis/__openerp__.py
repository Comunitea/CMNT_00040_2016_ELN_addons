# -*- coding: utf-8 -*-
# Copyright 2017 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Pack Operation Analysis",
    "summary": "Analysis view for stock pack operation",
    "version": "8.0.1.0.0",
    "category": "Inventory, Logistic, Storage",
    "website": "https://www.elnogal.com",
    "author": "Pedro Gómez",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        'report/stock_pack_operation_analysis_view.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
}
