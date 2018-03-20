# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields
import openerp.addons.decimal_precision as dp





class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    @api.multi
    def get_package_info(self):
        for package in self:
            if package.children_ids:
                package.multi = True
                package.product_id = False
                package.package_qty = 0.00
                lot_id = False
            else:
                package.multi = False
                package.package_qty = sum(quant.qty for quant in package.quant_ids)
                package.product_id = package.quant_ids and package.quant_ids[0].product_id or False
                package.lot_id = package.quant_ids and package.quant_ids[0].lot_id or False

    package_qty = fields.Float('Quantity',
                               digits_compute=dp.get_precision('Product Unit of Measure'),
                               compute=get_package_info, multi=True)
    product_id = fields.Many2one('product.product', 'Product', compute=get_package_info, multi=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot', compute=get_package_info, multi=True)
    multi = fields.Boolean('Multi', compute=get_package_info, multi=True)
    product_id_name = fields.Char(related='product_id.display_name')
    uom_id = fields.Many2one(related='product_id.uom_id')
    uom = fields.Char()

    @api.model
    def check_inter(self, old, new):
        return (old.product_id == new.product_id) and new.package_qty > 0

    @api.model
    def name_to_id(self, name):
        package = self.search([('name', '=', name)], limit=1)
        return package or False

    @api.model
    def get_app_fields(self, id):

        object_id = self.browse(id)
        fields = {}
        if object_id:
            for field in fields:
                fields[field] = object_id[field]
        return fields

class StockProductionLot(models.Model):

    _inherit = 'stock.production.lot'

    @api.multi
    def get_lot_location_id(self, location_id=False):
        for lot in self:
            if location_id:
                internal_quants = lot.quant_ids.\
                    filtered(lambda x: x.location_id.id == location_id and x.location_id.usage == 'internal')
            else:
                internal_quants = lot.quant_ids.\
                    filtered(lambda x: x.location_id.usage == 'internal')

            lot_qty = sum(internal_quants.mapped('qty'))
            lot.available_qty = lot_qty
            location_id = list(set(internal_quants.mapped('location_id').mapped('id')))
            if len(location_id) == 1:
                lot.location_id = location_id
            else:
                lot.location_id = False

    location_id = fields.Many2one('stock.location', compute="get_lot_location_id", multi=True)
    available_qty = fields.Float('Qty', compute="get_lot_location_id", multi=True)
    uom_id = fields.Many2one(related='product_id.uom_id')