# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "El Nogal Sale",
    "description": """Different sales customizations for El Nogal""",
    "version": "1.0",
    "author": "Pexego",
    "depends": [
        'base',
        'sale',
        'stock',
        'product',
        'sale_order_dates',
        'sale_early_payment_discount',
        'sale_commission',
        'eln_sale_commission',
        'account_payment_partner',
        'account_analytic_default',
    ],
    "category": "Sale",
    "init_xml": [],
    "data": [
        'views/account_invoice_view.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/stock_view.xml',
        'views/sale_shop_view.xml',
        'views/sale_workflow.xml',
        'security/ir.model.access.csv',
        'security/sale_security.xml',
        'wizard/sale_order_confirm_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
