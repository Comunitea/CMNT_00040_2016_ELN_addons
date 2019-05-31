# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    _order = 'sequence, min_quantity desc, name'

    price_calculated = fields.Float(
        string='Price calculated',
        digits=dp.get_precision('Product Price'),
        compute='_get_price_calculated', default=0.0)
    ean13 = fields.Char(string="EAN13", related='product_id.ean13', readonly=True)
    uom_id = fields.Many2one('product.uom', related='product_id.uom_id', string='UoM', readonly=True)
    uos_id = fields.Many2one('product.uom', related='product_id.uos_id', string='UoS', readonly=True)

    @api.multi
    def _get_price_calculated(self):
        """ return the price calculated if it's possible for price list item """
        for item in self:
            price = False
            product_id = item.product_id
            if item.product_id:
                pricelist = item.price_version_id.pricelist_id
                if pricelist:
                    qty = item.min_quantity
                    date_price = item.price_version_id.date_start or item.price_version_id.date_end 
                    price = pricelist.with_context(date=date_price).price_get(
                        product_id.id, qty or 1.0, partner=False)[pricelist.id]
            item.price_calculated = price or 0.0

