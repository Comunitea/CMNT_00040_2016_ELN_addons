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
    'name': "Sale Order Import",
    'version': '1.0',
    'category': 'Sale',
    'description': """Módulo que permite la importacion de pedidos de venta desde ficheros externos""",
    'author': 'Pedro Gómez',
    'website': 'www.elnogal.com',
    "depends" : ['sale',
                 'eln_custom',
                 'eln_sale',
                 'sale_commission',
                 'eln_partner_discount'
                 ],
    "init_xml" : [],
    'data': [
        'sale_order_import_view.xml',
    ],
    "demo_xml" : [],
    "active": False,
    "installable": True
}
