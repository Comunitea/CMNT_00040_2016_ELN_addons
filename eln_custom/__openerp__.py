# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Omar Castiñeira Saavedra$ <omar@pexego.es>
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
    "name": "El Nogal Custom",
    "description": """Different customizations for El Nogal""",
    "version": "1.0",
    "author": "Pexego",
    "depends": [
        'base',
        'product',
        'stock',
        'purchase',
        'sale',
        'hr',
        'eln_sale',
        'eln_purchase',
        'product_expiry',
        'account',
        'account_analytic_default',
        'account_analytic_plans',
        'acc_analytic_acc_distribution_between',
        'sale_early_payment_discount',
        'document',
        'l10n_es_partner',
        'l10n_es_account_balance_report',
        'account_asset',
        'picking_invoice_rel',
    ],
    "category": "Custom",
    "init_xml": [],
    "data": [
        'security/ir.model.access.csv',
        'security/eln_custom_security.xml',
        'data/balance_reporting_template.xml',
        'views/account_asset_view.xml',
        'views/product_view.xml',
        'views/res_partner_view.xml',
        'views/route_view.xml',
        'views/stock_view.xml',
        'views/base_custom.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
