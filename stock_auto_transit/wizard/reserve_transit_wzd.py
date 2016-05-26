# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class ReserveTransitWzd(models.TransientModel):
    _name = 'reserve.transit.wzd'

    date = fields.Date('Report Date', required=True,
                       default=fields.Date.today())

    @api.multi
    def reserve_transit(self, pick):
        t_quant = self.env['stock.quant'].sudo()
        wh_objs = self.env['stock.warehouse'].sudo().search([])
        stock_locs = [x.lot_stock_id for x in wh_objs]
        q2transit = {}
        for loc in stock_locs:
            q2transit = t_quant._search_negative_quants_qty(loc)
            for prod in q2transit:
                orig_loc_id = self.env['procurement.order'].\
                    _get_origin_location_route(prod, loc)
                if not orig_loc_id:
                    continue
                transit_moves = \
                    self._get_original_move_from_procurement(prod, orig_loc_id)

                for move in transit_moves:
                    lot_dic = q2transit[prod]
                    forced_quants = \
                        self.env['stock.move'].\
                        _get_quants_to_transit(move, lot_dic)
                    if forced_quants:
                        ctx = self._context.copy()
                        ctx.update(forced_quants=forced_quants)
                        orig_move = self.env['stock.move'].sudo().\
                            with_context(ctx).browse(move.id)
                        orig_move.action_assign()
        return

    @api.model
    def _get_original_move_from_procurement(self, prod, orig_loc_id):
        t_move_su = self.env['stock.move'].sudo()
        domain = [
            ('location_id', '=', orig_loc_id),
            ('product_id', '=', prod.id),
            ('location_dest_id.usage', '=', 'transit'),
            ('state', '=', 'confirmed')
        ]
        res = t_move_su.search(domain)
        return res
