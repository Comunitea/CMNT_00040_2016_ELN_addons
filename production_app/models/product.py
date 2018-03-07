# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields

QUALITY_TYPES = [
    ('start', 'Start Up'),
    ('freq', 'Frequency'),
]

VALUE_TYPES = [
    ('check', 'Check'),
    ('text', 'Text'),
    ('numeric', 'Numeric'),
]


class ProductProduct(models.Model):
    _inherit = 'product.product'

    quality_check_ids = fields.Many2many(
        'product.quality.check',
        rel='product_quality_check_product_rel',
        id1='product_id', id2='quality_id'
    )
    # quality_count = fields.Integer('# Qualñity Cjecks',
    #                                compute='_compute_quality_check')

    # @api.multi
    # def _compute_quality_check(self):
    #     for product in self:
    #         domain = [('product_id', '=', product.id)]
    #         pqc_objs = self.env['product.quality.check'].search(domain)
    #         product.quality_count = len(pqc_objs)


class ProductQualityChecks(models.Model):
    _name = 'product.quality.check'

    name = fields.Char('Name')
    # product_id = fields.Many2one('product.product', 'Product')
    product_ids = fields.Many2many(
        'product.product',
        rel='product_quality_check_product_rel',
        id1='quality_id', id2='product_id'
    )
    quality_type = fields.Selection(QUALITY_TYPES, 'Control Type')
    value_type = fields.Selection(VALUE_TYPES, 'Value Type')
    workcenter_id = fields.Many2one('mrp.workcenter', 'Work Center',
                                    readonly=False)
