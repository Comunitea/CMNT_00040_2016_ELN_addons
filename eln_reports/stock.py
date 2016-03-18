# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Javier Colmenero Fernández$
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
from openerp.osv import osv, fields

class stock_move(osv.osv):
    _inherit = 'stock.move'

    def _get_tax_line(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        for move in self.browse(cr, uid, ids):
            if move.purchase_line_id and move.purchase_line_id.taxes_id:
                res[move.id] = u', '.join(map(lambda x: x.name, move.purchase_line_id.taxes_id)).split("%")[0].split(" ")[-1]
            elif move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.tax_id:
                res[move.id] = u', '.join(map(lambda x: x.name, move.procurement_id.sale_line_id.tax_id)).split("%")[0].split(" ")[-1]
            else:
                res[move.id] = ""
        return res

    _columns = {
        'tax_line': fields.function(_get_tax_line, method=True, string="Tax line", readonly=True, type="char", size=255),
    }


class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns = {
        'out_report_ids': fields.one2many('out.picking.report', 'picking_id',
                                          'Delivery List', readonly=True)
    }
