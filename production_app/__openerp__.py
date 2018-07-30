# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Production App',
    'version': '8.0.0.0.0',
    'author': 'Comunitea ',
    "category": "Custom",
    'license': 'AGPL-3',
    'depends': [
        'eln_production',
    ],
    'contributors': [
        "Comunitea ",
        "Javier Colmenero <javier@comunitea.com>"
    ],
    "data": [
        'views/app_registry_view.xml',
        'views/mrp_view.xml',
        'views/product_view.xml',
        'views/stop_reason_view.xml',
        'views/scrap_reason_view.xml',
        'views/stock_view.xml',
        'data/app_data.xml',
        "security/ir.model.access.csv",
    ],
    "demo": [
    ],
    'test': [
    ],
    "installable": True
}
