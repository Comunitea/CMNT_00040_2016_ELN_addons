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
from openerp.osv import orm, fields
from openerp import models, api


class stock_warehouse(orm.Model):
    _inherit = "stock.warehouse"
    
#    Añadimos este check para indicar si el almacen es depósito.
    _columns = {
        'good_warehouse': fields.boolean('Good Warehouse', help="Check the good warehouse field if the warehouse is a good warehouse."),
    }


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    @api.multi
    def name_get(self):
        return [(pt.id, pt.warehouse_id.name + ' - ' + pt.name)
                for pt in self]
