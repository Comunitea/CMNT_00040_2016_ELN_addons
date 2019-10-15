# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Eln Sale reports xls',
    'version': '8.0.1.0.0',
    'author': 'Comunitea, ',
    "category": "Eln sale report",
    "description": "Eln Sale reports xls",
    'license': 'AGPL-3',
    'depends': [
        'base',
        'sale_stock',
        'report_xls',
        'stock_picking_valued',
        'eln_sale',
        'eln_account'
    ],
    'contributors': [
        "Javier Colmenero <javier@comunitea.com>"
    ],
    "data": [
        "wizard/eln_sale_report_xls_wzd_view.xml",
        "wizard/eln_salesman_summary_xls_wzd_view.xml",
        "report/eln_sale_report.xml"
    ],
    "demo": [
    ],
    'test': [
    ],
    "installable": True
}
