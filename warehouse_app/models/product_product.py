# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, models, fields
import openerp.addons.decimal_precision as dp

from openerp.exceptions import ValidationError

class ProductProduct(models.Model):

    _inherit = 'product.product'

    default_stock_location_id = fields.Many2one('stock.location', "Default stock location")
    #default_stock_location_id_name = fields.Char(related='default_stock_location_id.name')
    #uom_id_name = fields.Char(related='uom_id.name')

    @api.model
    def get_stock_location_id(self):
        if self._context.get('default_stock_location_id', False):
            return self.env['stock.location'].browse(self._context['default_stock_location_id']) or False

        if self.default_stock_location_id:
            return self.default_stock_location_id
        domain = [('product_id', '=', self.product_id), ('qty', '>', 0), ('location_id.usage', '=', 'internal')]
        newer_quant = self.env['stock.quant'].search(domain, limit=1, order='in_date desc')
        if newer_quant:
            return newer_quant.location_id

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    default_stock_location_id = fields.Many2one('stock.location', "Default stock location")

