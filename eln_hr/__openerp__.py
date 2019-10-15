# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
    'name': "El Nogal - Recursos Humanos",
    'version': '1.0',
    'category': 'Human Resources',
    'description': """Módulo que amplía la información de la ficha de empleado en recursos humanos""",
    'author': 'Pedro Gómez',
    'website': 'www.elnogal.com',
    "depends" : [
        'hr',
    ],
    "init_xml" : [],
    'data': [
        'security/eln_hr_security.xml',
        'security/ir.model.access.csv',
        'views/hr_view.xml',
    ],
    "demo_xml" : [],
    "active": False,
    "installable": True
}
