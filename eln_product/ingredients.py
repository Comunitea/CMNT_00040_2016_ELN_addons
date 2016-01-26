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
import openerp.addons.decimal_precision as dp


class ingredient(orm.Model):
    _name = 'product.ingredient'
    _order = 'product_qty desc'
    def _get_product_qty_percent(self, cr, uid, ids, field_name, arg, context):

        res = {}
        qty_total = 0.0
        for line in self.browse(cr, uid, ids, context=context):
            qty_total += line.product_qty

        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            if qty_total != 0:
                res[line.id] = (line.product_qty * 100) / qty_total

        return res

    _columns = {
        'name': fields.char('Name', size=256, required=True, translate=True),
        'product_parent_id': fields.many2one('product.product', 'Product Parent', required=True),
        'product_qty': fields.float('Product Qty', required=True, digits_compute=dp.get_precision('Product UoM')),
        'product_qty_percent': fields.function(_get_product_qty_percent, type="float", string="Qty(%)", readonly=True),
        'origin': fields.char('Origin',size=255, translate=True),
        'caliber': fields.char('Caliber', size=64, translate=True),
        'process': fields.char('Process', size=64, translate=True),
        'variety': fields.char('Variety', size=64, translate=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),        
    }
    def on_change_product_id(self, cr, uid, ids, product_id, context=None):
        
        res = {}
        if product_id:
            product_obj = self.pool.get('product.product').browse(cr, uid, product_id)
            res['name'] = product_obj.name

        return {'value': res}

