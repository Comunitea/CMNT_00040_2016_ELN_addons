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
    "name" : "Document management",
    "description" : """Document management""",
    "version" : "1.0",
    "author" : "Pexego",
    "depends" : ["base","auto_attach","account","stock","document"], #"a90_stock",
    "category" : "Alfa",
    "init_xml" : [],
    # "update_xml" : [
    #             'data/type_expedient_seq.xml',
    #             'data/expedient_seq.xml',
    #             'data/document_management_cron.xml',
    #             'data/temp_folder_data.xml',
    #             'expedient_view.xml',
    #             'rel_view.xml',
    #             'ir_attachment_view.xml',
    #             'auto_attach_view.xml',
    #             'res_log_expedient_view.xml',
    #
    #             'security/document_management_security.xml',
    #             'security/ir.model.access.csv',
    #            # 'stock_view.xml',
    #
    #
    #
    #                 ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
