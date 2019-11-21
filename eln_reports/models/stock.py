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
from openerp import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def compute_out_report_lines(self):
        res = {}
        pickings = self.filtered(
            lambda r: r.state == 'done' and r.picking_type_code != 'incoming')
        if pickings:
            sql = """
                SELECT
                    spo.product_id    AS product_id,
                    spo.lot_id        AS lot_id,
                    smol.move_id      AS move_id,
                    SUM(smol.qty)     AS product_qty,
                    spo.picking_id    AS picking_id
                FROM stock_pack_operation spo
                JOIN stock_move_operation_link smol
                    ON spo.id = smol.operation_id
                WHERE spo.product_id IS NOT NULL
                    AND spo.picking_id in %s
                GROUP BY
                    smol.move_id,
                    spo.product_id,
                    spo.lot_id,
                    spo.picking_id
            """
            self._cr.execute(sql, [pickings._ids])
            records = self._cr.fetchall()
            for record in records:
                product_id = self.env['product.product'].browse(record[0])
                lot_id = self.env['stock.production.lot'].browse(record[1])
                move_id = self.env['stock.move'].browse(record[2])
                product_qty = record[3] or 0.0
                picking_id = self.env['stock.move'].browse(record[4])
                tax_str = ''
                total = 0.0
                taxes = move_id.procurement_id.sale_line_id.tax_id.sorted(key=lambda r: r.amount, reverse=True)
                if taxes:
                    tax_str = ', '.join([x.name.split('%')[0].split(' ')[-1] for x in taxes if x.name])
                if move_id.procurement_id.sale_line_id:
                    total = move_id.order_price_unit * product_qty
                vals = {
                    'product_id': product_id,
                    'lot_id': lot_id,
                    'move_id': move_id,
                    'product_qty': product_qty,
                    'picking_id': picking_id,
                    'tax_str': tax_str,
                    'total': total,
                }
                if picking_id.id not in res:
                    res[picking_id.id] = []
                res[picking_id.id].append(vals)
        # Ordenamos por código, ean13, nombre, movimmiento y lote
        for pick in self:
            if pick.id not in res:
                res[pick.id] = []
            else:
                res[pick.id] = sorted(
                    res[pick.id], key=lambda a: (
                        a['product_id'].default_code, a['product_id'].ean13, a['product_id'].name, a['move_id'], a['lot_id']
                    )
                )
        return res
