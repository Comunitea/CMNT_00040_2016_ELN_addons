# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        inv_vals = super(StockPicking, self)._get_invoice_vals(key, inv_type, journal_id, move)
        sale = move.picking_id.sale_id
        if inv_type in ('out_invoice', 'out_refund'):
            if sale:
                inv_vals.update({
                    'commercial_route_id': sale.commercial_route_id.id,
                    })
            elif move.picking_id.partner_id:
                partner_id = move.picking_id.partner_id
                inv_vals.update({
                    'commercial_route_id': partner_id.commercial_route_id.id,
                    })
        return inv_vals
