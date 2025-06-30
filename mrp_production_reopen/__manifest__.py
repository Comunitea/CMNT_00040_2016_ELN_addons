# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Alejandro Núñez Liz$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# NO MIGRAR


{
        "name" : "Reabrir proceso de producción",
        "version" : "18.0.1.0.0",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "license" : "AGPL-3",
        "category" : "Enterprise Specific Modules",
        "description": """
            Este modulo permite reabrir la producción una vez finalizada, devolviendola a 'Listo para producir'. 
            Permite cambiar los valores de los productos a consumir y producidos.
            No modifica las fechas de producción.
            
            mrp_production_reopen.py
              - Modifica las columnas de product_qty, product_uos_qty y state. De forma que las dos primeras son editables en el nuevo estado Reopen.
              - action_reopen y action_redone mueven los productos ( tanto de la pestaña consumidos como finalizados ) de done a draft para que sean modificables y luego de draft a done.
            
        """,
        "depends" : ["base","stock","product","mrp"],
        # "init_xml" : [],
      #  "demo_xml" : [],
        # "update_xml" : ['mrp_production_view.xml'],
        "installable": True,
        'active': False

}
