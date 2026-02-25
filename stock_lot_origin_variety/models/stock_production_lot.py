# -*- coding: utf-8 -*-
# Copyright 2026 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    origin_country_ids = fields.Many2many(
        'res.country', string='Country of origin',
        rel='stock_lot_origin_country_rel',
        id1='lot_id', id2='country_id'
    )
    variety = fields.Char('Variety')

    @api.model
    def default_get(self, fields):
        res = super(StockProductionLot, self).default_get(fields)
        product_id = res.get('product_id')
        if product_id and not res.get('variety'):
            product_id = self.env['product.product'].browse(product_id)
            res['variety'] = product_id.product_tmpl_id.variety or False
        return res

    def _raise_if_invalid_origin(self):
        for lot in self:
            if not lot.product_id:
                continue
            allowed = lot.product_id.product_tmpl_id.origin_country_ids
            invalid = lot.origin_country_ids - allowed
            if allowed and invalid:
                raise exceptions.ValidationError(
                    _("Only the following countries are allowed for this product '%s': %s")
                    % (lot.product_id.display_name, ", ".join(allowed.mapped('name')))
                )

    @api.model
    def create(self, vals):
        lot = super(StockProductionLot, self).create(vals)
        lot._raise_if_invalid_origin()
        return lot

    @api.multi
    def write(self, vals):
        res = super(StockProductionLot, self).write(vals)
        if 'origin_country_ids' in vals or 'product_id' in vals:
            self._raise_if_invalid_origin()
        return res

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            product_tmpl_id = self.product_id.product_tmpl_id
            self.variety = product_tmpl_id.variety or False
            return {'domain': {'origin_country_ids': [('id', 'in', product_tmpl_id.origin_country_ids.ids)]}}
        self.variety = False
        return {'domain': {'origin_country_ids': []}}



