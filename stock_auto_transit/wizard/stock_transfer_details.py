# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api, fields


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    auto_transit = fields.Boolean('Auto Transit')

    def _prepare_packops_vals(self, prod, lot, qty):
        picking_ids = self._context.get('active_ids', [])
        picking = self.env['stock.picking'].browse(picking_ids[0])
        orig_loc = picking.move_lines[0].location_id
        dest_loc = picking.move_lines[0].location_dest_id
        vals = {
            'picking_id': picking.id,
            'product_id': prod.id,
            'product_uom_id': prod.uom_id.id,  # TODO Que pasa si se cambio
            'product_qty': qty,
            'lot_id': lot.id,
            'location_id': orig_loc.id,
            'location_dest_id': dest_loc.id,
            'result_package_id': False,
            'package_id': False,
            'from_negative_quant': True
        }
        return vals

    @api.model
    def default_get(self, fields):
        """
        """
        t_move_su = self.env['stock.move'].sudo()
        t_op = self.env['stock.pack.operation']
        t_quant = self.env['stock.quant']
        picking_ids = self._context.get('active_ids', [])
        picking = self.env['stock.picking'].browse(picking_ids[0])
        if picking.auto_transit and \
                picking.location_dest_id.usage == 'transit':
            # picking.do_unreserve()
            picking.pack_operation_ids.unlink()
            prod_ids = set()
            dest_loc = False
            for m in picking.move_lines:
                move = t_move_su.browse(m.id)
                if not dest_loc:
                    dest_loc = move.move_dest_id.location_dest_id
                prod_ids.add(move.product_id.id)
            prod_ids = list(prod_ids)
            if dest_loc and prod_ids:
                domain = [('product_id', 'in', prod_ids)]
                q2transit = t_quant.\
                    _search_negative_quants_qty(dest_loc, extra_domain=domain)
                for prod in q2transit:
                    for lot in q2transit[prod]:
                        qty = q2transit[prod][lot]
                        vals = self._prepare_packops_vals(prod, lot, qty)
                        t_op.create(vals)
        res = super(StockTransferDetails, self).default_get(fields)
        if picking.auto_transit and \
                picking.location_dest_id.usage == 'transit':
            res.update(auto_transit=True)
        t_op = self.env['stock.pack.operation']
        if res.get('item_ids', False):
            for item in res['item_ids']:
                pack_op = t_op.browse(item['packop_id'])
                if pack_op.from_negative_quant:
                    item.update(from_negative_quant=True)
        return res


class StockTransferDetailsItems(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    from_negative_quant = fields.Boolean('From negative Quant', readonly=True)
