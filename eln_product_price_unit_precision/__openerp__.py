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
    'name': "El Nogal Product Price Unit Precision",
    'version': '1.0',
    'category': 'Accounting & Finance',
    'description': """
Allows to specify independent decimal precision.
=================================================

This module allows to set custom precisions for price_unit for the following tables
* purchase
* sale
* invoice

for obvious reasons the price_units should have the same precision in all modules

OpenERP calculates
quantity * price_unit = value(net)
and this should return the same value in all objects

SO/PO and invoice should have the same precision to be consistent.
Invoice must have in any case the max(SO/PO precision)

    """,
    'author': 'Pedro Gómez',
    'website': 'www.elnogal.com',
    "depends" : [
                 'account',
                 'sale',
                 'purchase',
                ],
    "init_xml" : [],
    # "update_xml" : ['data/product_price_unit_precision_data.xml'],
    "demo_xml" : [],
    "active": False,
    "installable": True
}
