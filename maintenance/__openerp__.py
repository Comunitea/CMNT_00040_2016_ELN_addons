# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos All Rights Reserved
#    Copyright (C) 2015-2016 Comunitea Servicios Tecnológicos All Rights Reserved
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
    "name": 'Maintenance',
    "version": '8.0.1.0.0',
    "author": 'Pexego',
    "category": 'Generic Modules',
    "description": """
    This module provide: Maintenance functionality.
    """,
    "depends": [
        'hr',
    ],
    "init_xml": [],
    'data': [
        'security/maintenance_security.xml',
        'security/ir.model.access.csv',
        'wizard/cancel_maintenance_request_view.xml',
        'views/maintenance_element_view.xml',
        'views/maintenance_element_type_cron.xml',
        'views/maintenance_type_view.xml',
        'views/maintenance_request_sequence.xml',
        'views/maintenance_request_view.xml',
        'views/maintenance_order_sequence.xml',
        'views/maintenance_order_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
