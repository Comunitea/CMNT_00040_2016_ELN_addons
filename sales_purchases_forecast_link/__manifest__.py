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
        "name" : "Sales and Purchases Forecast Link",
        "version" : "1.0",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Sales / Purchases Forecast",
        "description":
        """
            Bridge module between sales_forecast and purchases_forecast.
            Explodes recursively the material list of products a sales forecast,
            sum by product (raw material) and makes a forecast of purchases.
        """,
        "depends" : [
            'base',
            # 'sales_forecast',
            # 'purchases_forecast',
            'mrp'
        ],
        # "init_xml" : [],
      #  "demo_xml" : [],
        # "data" : ['wizard/sales_purchase_forecast.xml'
        #     ],
        "installable": True,
        'active': False
}