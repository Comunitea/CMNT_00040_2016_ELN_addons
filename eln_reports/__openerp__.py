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
    'name': "El Nogal Reports",
    'version': '1.0',
    'category': '',
    'description': """Module that contents el nogal's reports""",
    'author': 'Pexego Sistemas Informáticos',
    'website': 'www.pexego.es',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'jasper_reports',
        'stock_picking_valued',
        'stock',
        'report_webkit',
        'delivery_route',
        'picking_invoice_rel',  # Por campo stock_move_id
        'eln_production',
        'product_expiry',
    ],
    'init_xml': [],
    'data': [
        'views/res_users_view.xml',
        'views/mrp_view.xml',
        'report/planning_report/planning_report_webkit_header.xml',
        'wizard/planning_report_wizard_view.xml',
        'wizard/purchase_order_report_wizard_view.xml',
        'wizard/product_datasheet_report_wizard_view.xml',
        'wizard/product_logistics_sheet_report_wizard_view.xml',
        'views/eln_reports.xml',
        'views/layouts_custom.xml',
        'views/valued_picking_report_custom.xml',
        'views/report_saleorder_proforma.xml',
     ],
    'demo_xml': [],
    'active': False,
    'installable': True
}
