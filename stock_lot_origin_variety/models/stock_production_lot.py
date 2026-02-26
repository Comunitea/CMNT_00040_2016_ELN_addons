# -*- coding: utf-8 -*-
# Copyright 2026 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    origin_country_ids = fields.Many2many(
        'res.country', string='Country of origin',
        rel='stock_lot_origin_country_rel',
        id1='lot_id', id2='country_id'
    )
    variety = fields.Char('Variety')

    @api.model
    def create(self, vals):
        lot = super(StockProductionLot, self).create(vals)
        if lot and lot.product_id and not vals.get('variety') and not lot.variety:
            domain = [
                ('product_id', '=', lot.product_id.id),
                ('variety', '!=', False),
                ('id', '!=', lot.id),
            ]
            last = self.env['stock.production.lot'].search(
                domain,
                order='create_date desc, id desc',
                limit=1,
            )
            if last.variety:
                lot.variety = last.variety
        return lot

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            self.variety = False
        else:
            domain = [
                ('product_id', '=', self.product_id.id),
                ('variety', '!=', False),
            ]
            if self.id and isinstance(self.id, int):
                domain.append(('id', '!=', self.id))
            last_lot = self.env['stock.production.lot'].search(
                domain,
                order='create_date desc, id desc',
                limit=1,
            )
            self.variety = last_lot.variety or False
