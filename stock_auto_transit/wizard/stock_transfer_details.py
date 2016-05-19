# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.model
    def default_get(self, fields):
        """
        Overwrited to get the secondary unit to the item line.
        We get conversions of product model if we are in a outgoing picking
        else we use supplier products model conversions.
        We check if product is variable weight or not
        """
        import ipdb; ipdb.set_trace()
        picking_ids = self._context.get('active_ids', [])
        picking = self.env['stock.picking'].browse(picking_ids[0])
        if picking.auto_transit:
            picking.do_unreserve()

        res = super(StockTransferDetails, self).default_get(fields)
        return res
