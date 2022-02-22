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
    'name': "El Nogal Productions",
    'version': '1.0',
    'category': '',
    'description': """Module that contents el nogal's productions""",
    'author': 'Pexego Sistemas Informáticos',
    'website': 'www.pexego.es',
    'license': 'AGPL-3',
    "depends": [
        'base',
        'product',
        'mrp',
        'stock',
        'mrp_operations',
        'stock_traceability_tree',
        'stock_traceability_tree_trace_mrp',
        'hr',
        'stock_lock_by_lot',
    ],
    "init_xml": [],
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ir_cron.xml',
        'data/stock_production_lot_seq.xml',
        'wizard/mrp_modify_consumption.xml',
        'wizard/mrp_product_produce_view.xml',
        'views/mrp_view.xml',
        'views/mrp_workflow.xml',
        'views/product_view.xml',
        'views/stock_view.xml',
        'report/mrp_workorder_analysis_view.xml',
    ],
    "demo_xml": [],
    "installable": True
}
