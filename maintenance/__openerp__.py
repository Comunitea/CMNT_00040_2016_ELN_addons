# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos All Rights Reserved
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
###############################################################################
{
    "name": "Mantenimiento",
    "version": "1.0",
    "depends": ["Department", "product", "analytic", "stock", "purchase",
                "l10n_es_account_asset", "survey", "hr_timesheet",
                "jasper_reports", "purchase_oferts"],
    "author": "Pexego",
    "category": "category",
    "description": """
    This module provide :
    """,
    'data': ["intervention_request_sequence.xml", "security/maintenance_security.xml",
                   "maintenance_element_view.xml", "maintenance_type_cron.xml",
                    "maintenance_type_view.xml", "work_order_sequence.xml", "wizard/cancel_intervention_request_view.xml",
                    "intervention_request_view.xml", "work_order_report.xml","work_order_view.xml",
                    "stock_view.xml","hr_view.xml", "purchase_view.xml", "maintenance_data.xml",
                    "security/ir.model.access.csv", "product_view.xml", "maintenance_stop_view.xml"],

    'installable': True,
    'active': False,
}
