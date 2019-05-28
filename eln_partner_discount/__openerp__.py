# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Omar Castiñeira Saavedra$ <omar@pexego.es>
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
    "name" : "El Nogal Partner Discount",
    "description" : """Includes a discount in partner view, this discount affetcs to sale order lines""",
    "version" : "1.0",
    "author" : "Pexego",
    "depends" : [
        'base',
        'product',
        'sale',
        'account',
        'eln_sale',
    ],
    "category" : "Sale",
    "init_xml" : [],
    "data" : [
        'views/res_partner_view.xml',
        'views/sale_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
