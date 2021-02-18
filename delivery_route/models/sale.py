# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_ship_create(self):
        res = super(SaleOrder, self).action_ship_create()
        for order in self:
            delivery_route_id = order.partner_shipping_id.delivery_route_id or \
                order.partner_shipping_id.commercial_partner_id.delivery_route_id
            vals = {
                'delivery_route_id': delivery_route_id.id,
                'loading_date': delivery_route_id.next_loading_date,
            }
            order.picking_ids.write(vals)
        return res
