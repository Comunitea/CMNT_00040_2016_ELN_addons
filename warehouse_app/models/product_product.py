# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, models, fields
import openerp.addons.decimal_precision as dp

from openerp.exceptions import ValidationError

class ProductProduct(models.Model):

    _inherit = 'product.product'


    @api.model
    def _get_product_quants(self):
        domain = [('product_id', '=', self.id), ('location_id.usage', '=', 'internal')]
        quant_ids = self.env['stock.quant'].search(domain)
        self.quant_ids = quant_ids

    default_stock_location_id = fields.Many2one('stock.location', "Default stock location")
    quant_ids = fields.One2many('stock.quant', compute="_get_product_quants")

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


    @api.multi
    def print_barcode_tag_report(self):
        self.ensure_one()
        custom_data = {
            'product_id': self.id,
        }
        rep_name = 'warehouse_app.product_tag_report'
        rep_action = self.env["report"].get_action(self, rep_name)
        rep_action['data'] = custom_data
        return rep_action

    @api.model
    def is_sustitutive(self, id):
        ##TODO DEFINIR CUALES SON SUSTITUTIVOS
        return True

    def _get_domain_locations(self, cr, uid, ids, context):

        domain = super(ProductProduct, self)._get_domain_locations(cr, uid, ids, context=context)
        force_domain = context.get('force_domain', False)
        if force_domain:
            print (force_domain + domain[0], domain[1], domain[2])
            return (force_domain + domain[0], domain[1], domain[2])
        else:
            return domain



class ProductTemplate(models.Model):

    _inherit = 'product.template'

    default_stock_location_id = fields.Many2one('stock.location', "Default stock location")

