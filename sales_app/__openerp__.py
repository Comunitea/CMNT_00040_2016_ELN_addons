# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2018 Comunitea
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
    "name": "Sales APP",
    "description": """Integration with Sales Android App""",
    "version": "1.0",
    "author": "Comunitea",
    "depends": [
        'sale',
        'sale_stock',
        'eln_sale',
        'commercial_route',
		'l10n_es_partner',
    ],
    "category": "Sale",
    "init_xml": [],
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/cron_table_data.xml',
        'views/res_company_view.xml',
        'views/table_pricelist_prices_view.xml',
        'views/pricelist_view.xml',
        'views/sale_order_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
