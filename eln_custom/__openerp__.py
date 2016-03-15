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
    "name" : "El Nogal Custom",
    "description" : """Different customizations for El Nogal""",
    "version" : "1.0",
    "author" : "Pexego",
    "depends" : ['base',
                'product',
                'stock',
                'purchase',
                'sale',
                'hr',
                # 'base_contact',
                'eln_sale',
                'eln_purchase',
                'product_expiry',
                'account',
                'account_analytic_default',
                'account_analytic_plans',
                'acc_analytic_acc_distribution_between',
                'sale_early_payment_discount',
                'eln_edi',
                'document',
                ],
    "category" : "Custom",
    "init_xml" : [],
    "data" : ['security/eln_custom_security.xml',
                   'security/ir.model.access.csv',
                   'route_view.xml',
                   'res_partner_view.xml',
                   'product_view.xml',
                   'stock_view.xml',
                   ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}

