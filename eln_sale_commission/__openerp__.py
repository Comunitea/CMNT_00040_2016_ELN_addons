# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Eln Sale Commissions',
    'version': '8.0.1.0.0',
    'author': 'Comunitea ',
    'category': 'Custom',
    'description': """
El Nogal Sale Commissions.
====================================

Add new features to sale commission module that covers:
--------------------------------------------
    * Add agents and commissions from delivery address
    * Cuatrimestral settlements
    * Default Agent commission property
    """,
    'license': 'AGPL-3',
    'depends': [
        'base',
        'sale_commission',
        'picking_invoice_rel'
    ],
    'contributors': [
        "Javier Colmenero Fernández <javier@comunitea.com>"
    ],
    "data": [
        'views/sale_order_view.xml',
        'views/res_partner_view.xml',
        'views/settlement_view.xml',
    ],
    "demo": [
    ],
    'test': [
    ],
    "installable": True
}
