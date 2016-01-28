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

# POST-MIGRATION: Se propaga el tipo de operación de la compra al albarán. Esto no es necesario
# class stock_picking(orm.Model):
#     _inherit = 'stock.picking'
#
#     def _get_warehouse(self, cr, uid, ids, field_name, args, context=None):
#         if context is None:
#             context = {}
#         res = {}
#         for picking in self.browse(cr, uid, ids, context=context):
#             res[picking.id] = picking.purchase_id and picking.purchase_id.warehouse_id and picking.purchase_id.warehouse_id.id or False
#
#         return res
#
#     _columns = {
#         'warehouse_id': fields.function(_get_warehouse, method=True, string='Warehouse', relation='stock.warehouse', type='many2one', store=True, readonly=True),
#     }


class stock_warehouse(orm.Model):
    _inherit = "stock.warehouse"
    
#    Añadimos este check para indicar si el almacen es depósito.
    _columns = {
        'good_warehouse': fields.boolean('Good Warehouse', help="Check the good warehouse field if the warehouse is a good warehouse."),
    }

