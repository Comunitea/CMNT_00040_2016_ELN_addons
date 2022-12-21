# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _get_product_quants(self):
        domain = [('product_id', '=', self.id), ('location_id.usage', '=', 'internal')]
        quant_ids = self.env['stock.quant'].search(domain)
        self.quant_ids = quant_ids

    quant_ids = fields.One2many('stock.quant', compute="_get_product_quants")
    pda_name = fields.Char("PDA name")

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

    def _get_domain_locations(self, cr, uid, ids, context):
        domain = super(ProductProduct, self)._get_domain_locations(cr, uid, ids, context=context)
        force_domain = context.get('force_domain', False)
        if force_domain:
            return (force_domain + domain[0], domain[1], domain[2])
        else:
            return domain
