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
    "depends" : ['base',
                'product',
                'mrp',
                'stock',
                'mrp_operations',
                'stock_traceability_tree',
                'stock_traceability_tree_trace_mrp',
                'hr',
                'mrp_production_reopen'
                ],
    "init_xml" : [],
    # "data" : ['data/product_data.xml',
    #                 'data/stock_production_lot_seq.xml',
    #                 'security/mrp_security.xml',
    #                 'mrp_workflow.xml',
    #                 'mrp_view.xml',
    #                 'product_view.xml',
    #                 'stock_production_lot_view.xml',
    #                 'security/ir.model.access.csv',
    #                 'stock_move_scrap_view.xml',
    #                 'stock_view.xml'
    #                 ],
    "demo_xml" : [],
    "active": False,
    "installable": True
}
