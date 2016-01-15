# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Pexego (<www.pexego.es>). All Rights Reserved
#    $Omar Castiñeira Saavedra$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    "name" : "Full Stock Traceability",
    "description" : """Full Stock Traceability for El Nogal""",
    "version" : "1.0",
    "author" : "Pexego",
    "depends" : ["base","stock","product","mrp","product_expiry","product_lot_sequence","procurement"],
    "category" : "Stock/Traceability",
    "init_xml" : [],
    # "update_xml" : ['security/ir.model.access.csv',
    #                 'stock_data.xml',
    #                 'product_view.xml',
    #                 'stock_location_view.xml',
    #                 'stock_move_view.xml',
    #                 'stock_partial_move_view.xml',
    #                 'mrp_production_view.xml',
    #                 'stock_production_lot_view.xml',
    #                 'procurement_view.xml',
    #                 'procurement_workflow.xml'
    #                 ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: