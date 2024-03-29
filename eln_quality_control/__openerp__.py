# -*- coding: utf-8 -*-
# Copyright 2020 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'eln_quality_control',
    'version': '8.0.1.0.0',
    'author': 'Pedro Gómez',
    'website': 'www.elnogal.com',
    'category' : 'Quality control',
    'description': """Different account customizations for El Nogal""",
    'depends': [
        'quality_control',
        'quality_control_mrp',
        'quality_control_stock',
    ],
    'data': [
        'data/quality_control_mrp_data.xml',
        'security/quality_control_security.xml',
        'security/ir.model.access.csv',
        'views/stock_pack_operation_view.xml',
        'views/stock_picking_view.xml',
        'views/stock_production_lot_view.xml',
        'views/qc_test_view.xml',
        'views/qc_inspection_view.xml',
        'wizard/mrp_production_generate_inspection.xml',
        'wizard/stock_picking_generate_inspection.xml',
    ],
    'installable': True,
    'images': [],
}
