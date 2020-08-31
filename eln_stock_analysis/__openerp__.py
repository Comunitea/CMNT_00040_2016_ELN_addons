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
        'product_expiry',
        'product_cost_management'
        # Dependency product_cost_management is only because this module redefines quant.cost field with digits precision.
        # If you update product_cost_management module after this one (e.g. with update=all) then the view is deleted
        # because field quant.cost is renamed to __temp_type_cast column (and finally dropped)
        # before add new quant.cost column to update new field.
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
