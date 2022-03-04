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
    'name' : "Performance calculation",
    'description': """
       Module for performance calculation: OEE = Availability * Performance * Quality.
        """,
    'version': '1.0',
    'author': 'Pexego',
    'depends': [
        'base',
        'product',
        'stock',
        'mrp',
        'eln_product',
        'eln_production',
        'eln_custom',
    ],
    'category': 'Manufacturing',
    'init_xml' : [],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/mrp_indicators_view.xml',
        'views/mrp_view.xml',
        'wizard/performance_calculation_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}