# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#    $Marta Vázquez Rodríguez$
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
    "name" : "Alfa90 document management",
    "description" : """Document management for Alfa90""",
    "version" : "1.0",
    "author" : "Pexego",
    "depends" : ["base", 'document_management', "jasper_reports", "base_report_to_printer", "account", "picking_invoice_rel", "board"],
    "category" : "Alfa",
    "init_xml" : [],
    "update_xml" : [
                #'wizard/print_final_expedient.xml',
                'expedient_invoices_view.xml',
                'account_invoice_view.xml',
                'expedient_view.xml',
                'security/ir.model.access.csv',
                'document_management_board.xml',
                'wizard/process_expedient_view.xml',
                'wizard/delete_invoice_expedient_view.xml'
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
