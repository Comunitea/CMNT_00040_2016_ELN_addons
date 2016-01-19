# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Comunitea Servicios Tecnológicos All Rights Reserved
#    $Omar Castiñeira Saaevdra <omar@comunitea.com>$
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
<<<<<<< HEAD:rappel_management/__openerp__.py
    "name" : "Rappel management",
    "description": """
        Module that adds rappel management.
        """,
    "version" : "1.0",
    "author" : "Pexego",
    "depends" : ["base", "sale"],
    "category" : "Generic Modules/Others",
    "init_xml" : [],
    "update_xml" : [ "wizard/rappel_renovation_view.xml",
                     "rappel_view.xml",
                     "res_partner_view.xml",
                     "security/ir.model.access.csv",
                     "rappel_wkf.xml",
                     ],
    'demo_xml': [],
=======
    'name': 'Rappel management',
    'author': 'Comunitea',
    'category': 'Sale',
    'website': 'www.comunitea.com',
    'description': """
Rappel Management
=====================================================

    """,
    'images': [],
    'depends': ['base',
                'account',
                'account',
                'stock',
                'product'],
    'data': ['rappel_type_view.xml',
             'rappel_view.xml',
             'res_partner_view.xml',
             'rappel_info_view.xml',
             'rappel_menus.xml',
             'rappel_mail_advice_data.xml',
             'data/ir.cron.xml',
             'wizard/compute_rappel_invoice_view.xml',
             'security/ir.model.access.csv'],
>>>>>>> d04ac55e200d3ddbab48b155e2860c9b4c7fbdea:rappel/__openerp__.py
    'installable': True,
    'application': True,
}
