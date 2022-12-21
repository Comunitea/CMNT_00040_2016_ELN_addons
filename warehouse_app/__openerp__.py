# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Warehouse App',
    'version': '8.0.0.0.0',
    'author': 'Kiko Sánchez',
    'category': 'Inventory, Logistic, Storage',
    'website': 'https://www.comunitea.com',
    'license': 'AGPL-3',
    'depends': [
        'stock',
        'eln_stock',
    ],
    'contributors': [
        'Comunitea',
        'Kiko Sánchez',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/warehouse_app_data.xml',
        'views/product_product.xml',
        'views/stock_picking.xml',
        'views/stock_location.xml',
        'views/stock_production_lot.xml',
        'views/stock_move.xml',
        'views/printing_printer.xml',
        "report/report.xml",
        "report/product_tag_report.xml",
        "report/location_tag_report.xml",
        "report/picking_list_report.xml"
    ],
    'installable': True
}
