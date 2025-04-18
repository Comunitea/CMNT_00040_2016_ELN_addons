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

# CREEN QUE NO SE USA

{
    "name" : "Multicompany stock transfers warehouse",
    "description": """
       Module that adds a wizard to make transfers of merchandise between companies.
        """,
    "version" : "1.0",
    "author" : "Pexego",
    "license" : "AGPL-3",
    # "depends" : ["base", "product", "stock", "procurement", "stock_location_templates", "eln_stock"],
    # "depends" : ["base", "product", "stock", "procurement", "eln_stock"], # Modificado post-migración
    "depends" : ["base", "product", "stock", "eln_stock"], # Modificado post-migración
    "category" : "Manufacturing",
    # "init_xml" : [],
    # "update_xml" : ["data/stock_data.xml",
    #                 "product_transfer_view.xml",
    #                 "security/product_transfers_security.xml",
    #                 "security/ir.model.access.csv"
    #                 ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
