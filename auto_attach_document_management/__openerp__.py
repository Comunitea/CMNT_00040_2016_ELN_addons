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
    "name" : "Alfa90 Auto attach document management",
    "description" : """Intermediate module between auto_attach and document_management""",
    "version" : "1.0",
    "author" : "Pexego",
    "depends" : ["base",'document_management','auto_attach', 'auto_attach_barcode'],
    "category" : "Alfa",
    "init_xml" : [],
    # "update_xml" : ["document_view.xml",
    #                 "document_workflow.xml",
    #                 "security/auto_attach_security.xml",
    #                 "security/ir.model.access.csv",
    #                 "auto_attach_workflow.xml",
    #                 "auto_attach_data.xml",
    #                 "wizard/manually_analyze_wzd_view.xml",
    #                 "scan_document_view.xml",
    #                 "scan_document_wkf.xml"
    #                 ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
