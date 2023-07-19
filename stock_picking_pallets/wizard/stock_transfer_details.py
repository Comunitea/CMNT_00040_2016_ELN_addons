# -*- coding: utf-8 -*-
# Copyright 2023 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class StockTransferDetailss(models.TransientModel):
    _inherit = 'stock.transfer_details'

    pallet_type_1 = fields.Integer('B1208A-Pallet CHEP 800x1200')
    pallet_type_2 = fields.Integer('P0604A-Pallet CHEP 400x600')
    pallet_type_3 = fields.Integer('Pallet IPP 800x1200')
    pallet_type_9 = fields.Integer('Others types of pallets')
    transport_company_pallets = fields.Integer('Transport company pallets')
    
    @api.model
    def default_get(self, fields):
        res = super(StockTransferDetailss, self).default_get(fields)
        picking_ids = self._context.get('active_ids', [])
        pallet_type_1 = pallet_type_2 = pallet_type_3 = pallet_type_9 = 0
        transport_company_pallets = 0
        if picking_ids:
            picking_id = self.env['stock.picking'].browse(picking_ids[0])
            pallet_type_1 = picking_id.pallet_type_1
            pallet_type_2 = picking_id.pallet_type_2
            pallet_type_3 = picking_id.pallet_type_3
            pallet_type_9 = picking_id.pallet_type_9
            transport_company_pallets = picking_id.transport_company_pallets
        res.update(
            pallet_type_1=pallet_type_1,
            pallet_type_2=pallet_type_2,
            pallet_type_3=pallet_type_3,
            pallet_type_9=pallet_type_9,
            transport_company_pallets=transport_company_pallets,
        )
        return res

    @api.multi
    def do_detailed_transfer(self):
        res = super(StockTransferDetailss, self).do_detailed_transfer()
        for wzd in self:
            if self.pallet_type_1 > 0 and wzd.picking_id.pallet_type_1 != self.pallet_type_1:
                wzd.picking_id.pallet_type_1 = self.pallet_type_1
            if self.pallet_type_2 > 0 and wzd.picking_id.pallet_type_2 != self.pallet_type_2:
                wzd.picking_id.pallet_type_2 = self.pallet_type_2
            if self.pallet_type_3 > 0 and wzd.picking_id.pallet_type_3 != self.pallet_type_3:
                wzd.picking_id.pallet_type_3 = self.pallet_type_3
            if self.pallet_type_9 > 0 and wzd.picking_id.pallet_type_9 != self.pallet_type_9:
                wzd.picking_id.pallet_type_9 = self.pallet_type_9
            if self.transport_company_pallets > 0 and wzd.picking_id.transport_company_pallets != self.transport_company_pallets:
                wzd.picking_id.transport_company_pallets = self.transport_company_pallets
        return res

