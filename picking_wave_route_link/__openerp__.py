# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Stock Picking Wave Route Link',
    'version': '8.0.1.0.0',
    'author': 'Comunitea ',
    "category": "Stock",
    'license': 'AGPL-3',
    'depends': [
        'stock_picking_wave',
        'eln_custom',
    ],
    'contributors': [
        "Kiko Sánchez <kiko@comunitea.com>"
    ],
    "data": [
        'views/stock_picking_wave.xml',
        'views/stock_picking.xml',
        'views/route.xml',
        'wizard/wzd_picking_wave_route_link.xml',
        'security/ir.model.access.csv',
        #'data/picking_wave_sequence.xml'
    ],
    "demo": [
    ],
    'test': [
    ],
    "installable": True
}
