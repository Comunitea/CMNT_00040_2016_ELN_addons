# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    commercial_route_id = fields.Many2one(
        string='Commercial route',
        comodel_name='commercial.route',
        domain="[('user_id', '=', user_id)]")

    @api.multi
    def onchange_delivery_id(self, company_id, partner_id, delivery_id, fiscal_position):
        res = super(SaleOrder, self).onchange_delivery_id(
                company_id, partner_id, delivery_id, fiscal_position)
        partner_ship = self.env['res.partner'].browse(delivery_id)
        res['value']['commercial_route_id'] = partner_ship.commercial_route_id.id
        return res

    @api.model
    def _prepare_invoice(self, order, lines):
        inv_vals = super(SaleOrder, self)._prepare_invoice(order, lines)
        inv_vals.update({
            'commercial_route_id': order.commercial_route_id.id,
            })
        return inv_vals
