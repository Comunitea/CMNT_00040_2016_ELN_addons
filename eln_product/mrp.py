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
from osv import osv, fields

class mrp_bom(osv.osv):
    _inherit = 'mrp.bom'
    def _get_product_qty_percent(self, cr, uid, ids, field_name, arg, context):

        res = {}
        qty_total = 0.0
        for line in self.browse(cr, uid, ids, context=context):

            qty_total += line.product_qty

        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = int(round((line.product_qty * 100) / qty_total))

        return res

    _columns = {
        'product_qty_percent': fields.function(_get_product_qty_percent, type="integer", string="Qty(%)", readonly=True),
    }
mrp_bom()