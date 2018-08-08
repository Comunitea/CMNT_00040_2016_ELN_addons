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
        return  super(StockTransferDetails, self.with_context(ctx)).do_detailed_transfer()


    #@api.model
    #def default_get(self, fields):
    #    res = super(StockTransferDetails, self).default_get(fields)

