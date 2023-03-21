# -*- coding: utf-8 -*-
# Copyright 2023 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=80):
        purchase_order = self._context.get('purchase_order', False)
        if purchase_order and name and name[0] == '*':
            name = name[1:]
            domain = args + ['|', ('seller_ids.product_code', 'ilike', name), ('name', operator, name)]
            prodids = self.search(domain, limit=limit)
            if prodids:
                res = prodids.name_get()
                if res:
                    return res
        res = super(ProductProduct, self).name_search(name=name, args=args, operator=operator, limit=limit)
        return res

    @api.multi
    def name_get(self):
        res = super(ProductProduct, self).name_get()
        default_sourceloc_id = self._context.get('default_sourceloc_id', False)
        default_destinationloc_id = self._context.get('default_destinationloc_id', False)
        if default_sourceloc_id and default_destinationloc_id:
            # Se da en el wizard de transferencia de albarán
            usage = self.env['stock.location'].browse(default_sourceloc_id).usage
            if usage == 'supplier':
                new_res = []
                for product_id in self:
                    default_code = product_id.default_code
                    name = product_id.name
                    product_code = product_id.seller_ids and product_id.seller_ids[0].product_code or ''
                    if product_code:
                        new_name = "[%s][%s] %s" % (default_code, product_code, name)
                    else:
                        new_name = "[%s] %s" % (default_code, name)
                    new_res.append((product_id.id, new_name))
                    res = new_res
        return res
