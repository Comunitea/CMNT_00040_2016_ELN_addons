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
    'name': "El Nogal Productions Merge",
    'version': '1.0',
    'category': '',
    'description': """Adds a new wizard that allows merging two or more production orders""",
    'author': 'Pexego Sistemas Informáticos',
    'website': 'www.pexego.es',
    "depends" : ['base',
                 'product',
                 'mrp',
                 'stock',
                 'mrp_operations',
                ],
    "init_xml" : [],
    "update_xml" : ["wizard/mrp_production_merge_view.xml"
                    ],
    "demo_xml" : [],
    "active": False,
    "installable": True
}
