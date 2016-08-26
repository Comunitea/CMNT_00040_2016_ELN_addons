# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2016 QUIVAL, S.A. All Rights Reserved
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
    "name": "Product Price History Analysis",
    "summary": "Analysis view for product price history",
    "version": "8.0.1.0.0",
    "category": "Inventory, Logistic, Storage",
    "website": "https://www.elnogal.com",
    "author": "Pedro Gómez",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends" : ['base',
                'product',
                'mrp',
                ],
    "data": [
        'report/product_price_history_analysis_view.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
}
