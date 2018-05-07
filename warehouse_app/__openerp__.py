# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Warehouse App",
    "summary": "Warehouse app",
    "version": "8.0.1.0.0",
    "category": "Inventory, Logistic, Storage",
    "website": "https://www.comunitea.com",
    "author": "Kiko Sánchez",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock", 
        "stock_picking_wave",
        "base_report_to_printer"
    ],
    "data": [
        'views/stock_picking.xml',
        'views/stock_location.xml',
        'views/stock_quant_package.xml',
        'views/stock_location_rack.xml',
        'views/stock_move.xml',
        'views/stock_picking_wave.xml',
        'views/printing_printer.xml',
        'views/stock_move_consume_wzd.xml'
        #"report/report.xml",
        #"report/product_tag_report.xml",
        #"report/location_tag_report.xml",
    ],
}
