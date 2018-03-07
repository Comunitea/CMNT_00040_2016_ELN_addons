# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields

class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"


    #lot_id_name = fields.Char(related='lot_id.name')
    #location_id_name = fields.Char(related='location_id.name')
    #product_id_name = fields.Char(related='product_id.name')
    uom = fields.Char(related='product_id.uom_id.name')

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