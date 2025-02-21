# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Marta Vázquez Rodríguez$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    sales_count = fields.Integer(compute='_sales_count') # Redefine compute method

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=80):
        res = super(ProductProduct, self).name_search(name=name, args=args, operator=operator, limit=limit)
        prodpart = self.env['partner.product']
        if name and self._context.get('partner_id', False):
            prodids = prodpart.search([('partner_id', '=', self._context.get('partner_id')), ('name', '=', name)], limit=limit)
            if prodids:
                products = prodids.mapped('product_id')
                res = products.name_get()
        return res

    @api.multi
    def _sales_count(self):
        r = dict.fromkeys(self.ids, 0)
        domain = [
            ('state', 'in', ['confirmed', 'done']),
            ('product_id', 'in', self.ids),
        ]
        res = self.env['sale.order.line'].read_group(domain, ['product_id', 'product_uom_qty', 'product_uom'], ['product_id', 'product_uom'], lazy=False)
        for group in res:
            from_unit = group['product_uom'][0]
            to_unit = self.browse(group['product_id'][0]).uom_id.id
            uom_qty = group['product_uom_qty']
            if from_unit != to_unit:
                uom_qty = self.env['product.uom']._compute_qty(from_unit, group['product_uom_qty'], to_unit)
            r[group['product_id'][0]] += uom_qty
        for product in self:
            product.sales_count = r[product.id]
