# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Eln Stock Analysis',
    'version': '8.0.1.0.0',
    'author': 'Pedro Gómez',
    'category': 'Custom',
    'description': """Different stock analysis customizations for El Nogal""",
    'license': 'AGPL-3',
    'depends': [
        'stock_analysis',
        'product_expiry'
    ],
    "data": [
        'report/stock_analysis_view.xml',
    ],
    "demo": [
    ],
    'test': [
    ],
    "installable": True
}
