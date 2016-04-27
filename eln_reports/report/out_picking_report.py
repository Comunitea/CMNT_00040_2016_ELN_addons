# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos All Rights Reserved
#    $Javier Colmenero Fernández$ <javier@pexego.es>
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

from openerp import tools
from openerp.osv import fields, osv


class out_picking_report(osv.osv):
    _name = "out.picking.report"
    _description = "Group products and lots in outgoing pickings"
    _auto = False
    _rec_name = 'product_id'
    # _order = 'sequence'

    def _get_total_price(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            if line.move_id.procurement_id.sale_line_id:
                res[line.id] = line.move_id.order_price_unit * line.product_qty
            else:
                res[line.id] = 0.0
        return res


    _columns = {
        'product_id': fields.many2one('product.product', 'Product',
                                      readonly=True),
        'reference': fields.related('product_id', 'default_code', type='char',
                                    string='Reference', size=128,
                                    readonly=True),
        'ean13': fields.related('product_id', 'ean13', type='char',
                                string='EAN 13', size=128, readonly=True),
        'lot_id': fields.many2one('stock.production.lot', 'Lot',
                                  readonly=True),
        'product_qty': fields.float('Quantity', readonly=True),
        'picking_id': fields.many2one('stock.picking', 'Wave', readonly=True),
        'move_id': fields.many2one('stock.move', 'Move', readonly=True),
        'total':fields.function(_get_total_price, type='float', string="total"),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR replace VIEW %s
AS
  (SELECT row_number() over ()          AS id,
          SQ.product_id       AS product_id,
          SQ.lot_id           AS lot_id,
          SQ.move_id          AS move_id,
          SUM(SQ.product_qty) AS product_qty,
          SQ.picking_id       AS picking_id
   FROM   (SELECT smol.operation_id    AS id,
                  quant.product_id     AS product_id,
                  quant.lot_id         AS lot_id,
                  quant.reservation_id AS move_id,
                  SUM(quant.qty)       AS product_qty,
                  move.picking_id      AS picking_id
           FROM   stock_quant quant
                  inner join stock_move move
                          ON move.id = quant.reservation_id
                  left outer join stock_move_operation_link smol
                               ON smol.reserved_quant_id = quant.id
           WHERE  quant.reservation_id IS NOT NULL
           GROUP  BY quant.product_id,
                     quant.lot_id,
                     quant.reservation_id,
                     move.picking_id,
                     smol.operation_id
           UNION
           SELECT Min(OP.id)          AS id,
                  OP.product_id       AS product_id,
                  OP.lot_id           AS lot_id,
                  smol.move_id        AS move_id,
                  SUM(smol.qty) AS product_qty,
                  p.id                AS picking_id
           FROM   stock_pack_operation OP
                  inner join stock_picking P
                          ON P.id = OP.picking_id
                  inner join stock_move_operation_link smol
                          ON OP.id = smol.operation_id
           WHERE  OP.product_id IS NOT NULL
           GROUP  BY OP.product_id,
                     OP.lot_id,
                     smol.move_id,
                     P.id) SQ
   GROUP  BY SQ.product_id,
             SQ.lot_id,
             SQ.move_id,
             SQ.picking_id) """ % self._table)
