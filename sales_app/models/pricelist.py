# -*- coding: utf-8 -*-
# Copyright 2020 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    in_app = fields.Boolean('Pricelist in APP', default=False)

    @api.model
    def _price_rule_get_multi(self, pricelist, products_by_qty_by_partner):
        if self._context.get('from_sales_app', False):
            date = self._context.get('date') or fields.Date.context_today(self)
            date = date[0:10]
            products = map(lambda x: x[0], products_by_qty_by_partner)
            if not products:
                return {}
            version = False
            for v in pricelist.version_id:
                if ((v.date_start is False) or (v.date_start <= date)) and ((v.date_end is False) or (v.date_end >= date)):
                    version = v
                    break
            if not version:
                res = {}
                for product in products:
                    res[product.id] = (False, False)
                return res
        return super(ProductPricelist, self)._price_rule_get_multi(pricelist, products_by_qty_by_partner)


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    app_discount1 = fields.Float('Discount 1',
        digits=(16,2), default=0.0,
        help="Discount to apply from sales app")
    app_discount2 = fields.Float('Discount 2',
        digits=(16,2), default=0.0,
        help="Discount to apply from sales app")
    app_discount3 = fields.Float('Discount 3',
        digits=(16,2), default=0.0,
        help="Discount to apply from sales app")
