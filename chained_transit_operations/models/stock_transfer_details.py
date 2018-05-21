# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields

from openerp.exceptions import ValidationError


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'


    @api.one
    def do_detailed_transfer(self):
        for line in self.item_ids:
            if line.destinationloc_id.in_pack and not line.result_package_id:
                line.result_package_id = self.env['stock.quant.package'].create({})
        ctx = self._context.copy()
        ctx.update(force_sudo=True)
        res = super(StockTransferDetails, self.with_context(ctx)).do_detailed_transfer()
        if self._context.get('no_transfer', True):
            for op in self.picking_id.pack_operation_ids:
                op.picking_order = op.location_id.picking_order
        return res


    @api.model
    def default_get(self, fields):
        res = super(StockTransferDetails, self).default_get(fields)
        if self._context.get('from_cross_company', False):
            final_location_dest_id = self._context.get('final_location_dest_id', False)
            for item in res['item_ids']:
                item['final_location_dest_id'] = final_location_dest_id
            for item in res['packop_ids']:
                item['final_location_dest_id'] = final_location_dest_id
        return res