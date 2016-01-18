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
    "name" : "Picking Invoice Price Unit",
    "description" : """Modifica el método que se usa para obtener el precio unitario cuando se genera la factura desde un albarán. 
Si existe pedido de venta o pedido de compra se obtiene el precio unitario indicado en el pedido de venta o compra.
En caso contrario se obtendrá de la tarifa de venta o compra del clinte o proveedor y en su defecto del producto (precio venta o coste).""",
    "version" : "1.0",
    "author" : "Pedro Gómez",
    # "depends" : ["base","stock","sale", "purchase","purchase_landed_costs"], #Muy importante tener de dependecias todos los modulos donde se herede _get_price_unit_invoice
    "depends" : ["base","stock","sale", "purchase"], # Modificado por fallo post-migración
    "category" : "Stock",
    "init_xml" : [],
    "update_xml" : [],
    'demo_xml': [],
    "website": 'http://www.elnogal.com',
    'installable': True,
    'active': False,
}
