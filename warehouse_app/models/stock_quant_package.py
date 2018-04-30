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

    @api.model
    def get_available_packages(self, vals):
        product_id = vals.get('product_id')
        qty = vals.get('qty')
        domain = [('product_id', '=', product_id), ('multi', '=', False), ('quant_ids', '!=', [])]
        packages = []
        package_ids = self.env['stock.quant.package'].search(domain)

        for package_id in package_ids:
            vals = {'id': package_id.id,
                    'display_name': package_id.display_name,
                    'package_qty': package_id.package_qty,
                    'location_id': package_id.location_id and package_id.location_id.name,
                    'lot_id': package_id.lot_id.name}
            packages.append(vals)
        return packages


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
            internal_quants = lot.quant_ids.filtered(lambda x: (x.location_id.usage == 'internal'))
            if internal_quants:
                lot.location_id = internal_quants[0].location_id

    @api.model
    def get_available_lot(self, vals):
        product_id = vals.get('product_id')
        qty = vals.get('qty')
        op_id = vals.get('op_id', 0)
        domain = [('product_id', '=', product_id)]
        lots = []
        lot_ids = self.env['stock.production.lot'].search(domain).filtered(lambda x: x.virtual_available >= qty or x.id == op_id)
        print lot_ids
        for lot_id in lot_ids:
            vals = {'id': lot_id.id,
                    'display_name': lot_id.display_name,
                    'virtual_available': lot_id.virtual_available,
                    'qty_available': lot_id.qty_available,
                    'location_id': lot_id.location_id and lot_id.location_id.name,
                    'use_date': lot_id.use_date}
            lots.append(vals)
        return lots


    @api.multi
    def _get_virtual_available(self):
        for lot in self:
            location_ids = [w.view_location_id.id for w in self.env['stock.warehouse'].search([])]
            lot.virtual_available = lot.sudo().product_id.with_context(lot_id=lot.id, location=location_ids,
                                                                       force_domain=[('reservation_id','=',False)]).qty_available

    location_id = fields.Many2one('stock.location', compute="get_lot_location_id")
    uom_id = fields.Many2one(related='product_id.uom_id')
    virtual_available = fields.Float(
        compute='_get_virtual_available',
        type='float',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        string='Not reserved qty')
