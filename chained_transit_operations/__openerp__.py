# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Chained Transit Operations",
    "summary": "Link chained moves, and pre-reserved qties in move",
    "version": "8.0.1.0.0",
    "category": "Stock",
    "website": "https://www.comunitea.com",
    "author": "Kiko Sánchez",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock", "stock_auto_transit"
    ],
    "data": [
        'views/stock_move.xml',
        'views/stock_picking.xml',
        'views/res_company.xml',
        'wizard/wzd_sale_order_cancel.xml'
    ],
}
