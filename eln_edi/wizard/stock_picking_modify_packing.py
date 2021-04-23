# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class StockPickingModifyPacking(models.TransientModel):
    _inherit = 'stock.picking.modify.packing'

    @api.model
    def default_get(self, fields):
        res = super(StockPickingModifyPacking, self).default_get(fields)
        picking_id = self._context.get('active_id', False)
        picking = self.env['stock.picking'].browse(picking_id)
        if not picking.packing_ids:
            pack_ul_id = self.env['product.ul'].search(
                [('edi_code', '=', '201')], limit=1)
            res.update(pack_ul_id=pack_ul_id.id)
        return res
