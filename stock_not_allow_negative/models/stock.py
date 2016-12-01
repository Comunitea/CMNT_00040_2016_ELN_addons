# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2016 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp import api, _, exceptions, models, fields


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _quant_create(self, qty, move, lot_id=False, owner_id=False,
                      src_package_id=False, dest_package_id=False,
                      force_location_from=False, force_location_to=False):
        deny = True
        deny = deny and move.product_id.type == 'product'
        deny = deny and move.location_id.usage == 'internal'
        deny = deny and move.location_id.allow_negative_stock != 'always'
        deny = deny and (move.location_id.allow_negative_stock == 'never' or
                        (move.location_id.allow_negative_stock in ('by_product', False) and not move.product_id.allow_negative_stock))
        if deny:
            lot_msg_str = ""
            if lot_id:
                lot = self.env['stock.production.lot'].browse(lot_id)
                lot_msg_str = _("with the Lot/Serial '%s' ") % lot.name_get()[0][1]
            raise exceptions.Warning(_('Invalid Action!'), _(
                "There is not enough stock for product\n'%s'"
                "\n%sin location '%s'."
                "\nNegative stock is not allowed for this product."
            ) % (move.product_id.name_get()[0][1],
                 lot_msg_str,
                 move.location_id.display_name,))
        return super(StockQuant, self)._quant_create(
            qty, move, lot_id=lot_id, owner_id=owner_id,
            src_package_id=src_package_id, dest_package_id=dest_package_id,
            force_location_from=force_location_from,
            force_location_to=force_location_to)


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.model
    def _search(self, args, offset=0, limit=0, order=None, count=False, access_rights_uid=None):
        if self._context.get('product_id', False) and self._context.get('location_id', False):
            product_id = self.env['product.product'].browse(self._context.get('product_id', False))
            location_id = self.env['stock.location'].browse(self._context.get('location_id', False))
            restrict_search = True
            restrict_search = restrict_search and product_id.type == 'product'
            restrict_search = restrict_search and location_id.usage == 'internal'
            restrict_search = restrict_search and location_id.allow_negative_stock != 'always'
            restrict_search = restrict_search and (location_id.allow_negative_stock == 'never' or
                            (location_id.allow_negative_stock in ('by_product', False) and not product_id.allow_negative_stock))
            if restrict_search:
                stock_ids = [x.lot_stock_id.id
                             for x in self.env['stock.warehouse'].search([])]
                is_stock = self.env['stock.location'].search(
                    [('id', 'child_of', stock_ids), ('id', '=', self._context.get('location_id', False))])
                if is_stock:
                    quants = self.env['stock.quant'].search(
                        [('location_id', '=', self._context.get('location_id')),
                         ('product_id', '=', self._context.get('product_id')),
                         ('lot_id', '!=', False)])
                    lot_ids = [x.lot_id.id for x in quants]
                    args = [('id', 'in', lot_ids)] + args
        return super(StockProductionLot, self)._search(
            args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)

    @api.multi
    def name_get(self):
        res = super(StockProductionLot, self).name_get()
        if res and self._context.get('product_id', False) and self._context.get('location_id', False):
            product_id = self.env['product.product'].browse(self._context.get('product_id', False))
            location_id = self.env['stock.location'].browse(self._context.get('location_id', False))
            show_stock = True
            show_stock = show_stock and product_id.type == 'product'
            show_stock = show_stock and location_id.usage == 'internal'
            show_stock = show_stock and location_id.allow_negative_stock != 'always'
            show_stock = show_stock and (location_id.allow_negative_stock == 'never' or
                            (location_id.allow_negative_stock in ('by_product', False) and not product_id.allow_negative_stock))
            if show_stock:
                stock_ids = [x.lot_stock_id.id
                             for x in self.env['stock.warehouse'].search([])]
                is_stock = self.env['stock.location'].search(
                    [('id', 'child_of', stock_ids), ('id', '=', self._context.get('location_id', False))])
                if is_stock:
                    new_res = []
                    for lot_id, lot_name in res:
                        quants = self.env['stock.quant'].search(
                            [('location_id', '=', self._context.get('location_id')),
                             ('product_id', '=', self._context.get('product_id')),
                             ('lot_id', '=', lot_id)])
                        lot_qty = sum(x.qty for x in quants)
                        new_name = "%s (%s)" % (lot_name, lot_qty)
                        new_res.append((lot_id, new_name))
                    res = new_res
        return res

class StockLocation(models.Model):
    _inherit = 'stock.location'

    allow_negative_stock = fields.Selection([
        ('by_product', 'By product'), 
        ('always', 'Always'), 
        ('never', 'Never')], string="Allow negative stock", 
        default='by_product',
        help="This field only applies to stockables products and internal locations.\n"
        "\nBy product: Negative stocks will only be allowed on products with the 'Allow negative stock' field enabled."
        "\nAlways: Negative stocks will always be allowed."
        "\nNever: Negative stocks will never be allowed.")
