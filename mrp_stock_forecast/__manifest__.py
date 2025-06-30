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
# NO MIGRAR
{
        "name" : "MRP-Stock forecast",
        "version" : "18.0.1.0.0",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "license": "AGPL-3",
        "category" : "Manufacturing",
        "description": """MRP Stock forecast""",
        "depends" : [
            'mrp',
            'base', 
            'stock', 
        ],
        # "init_xml" : [],
      #  "demo_xml" : [],
        # "data" : ['security/ir.model.access.csv',
        #           'security/security.xml',
        #           'mrp_forecast_view.xml',
        #           'stock_forecast_view.xml',
        #           'wizard/merge_forecasts_view.xml',
        #     ],
        "installable": True,
        'active': False

}
