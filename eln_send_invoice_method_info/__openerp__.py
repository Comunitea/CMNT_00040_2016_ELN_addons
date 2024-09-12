# -*- coding: utf-8 -*-
# Copyright 2024 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'eln_send_invoice_method_info',
    'version': '1.0',
    'author': 'Pedro Gómez',
    'website': 'www.elnogal.com',
    'category' : 'Accounting & Finance',
    'description': """Show info of invoices send method""",
    'depends': [
        'account',
    ],
    'data': [
        'views/account_invoice_view.xml',
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'images': [],
}
