# -*- coding: utf-8 -*-
# Copyright 2019 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Stock Picking Export",
    'version': '1.0',
    'category': 'Warehouse Management',
    'description': """Módulo que permite la exportación de albaranes a fichero de texto""",
    'author': 'Pedro Gómez',
    'website': 'www.elnogal.com',
    "depends" : [
        'sale',
        'stock',
        'sale_stock',
        'product_expiry',
        'account_payment_sale',
        'sale_early_payment_discount',
        'eln_sale',
        'eln_reports',
     ],
    "init_xml" : [],
    'data': [
        'stock_picking_export_view.xml',
    ],
    "demo_xml" : [],
    "active": False,
    "installable": True
}
