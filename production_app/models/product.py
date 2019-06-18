# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields

QUALITY_TYPES = [
    ('start', 'Start Up'),
    ('freq', 'Frequency'),
]

VALUE_TYPES = [
    ('check', 'Check'),
    ('text', 'Text'),
    ('numeric', 'Numeric'),
    ('barcode', 'Bar Code'),
]

BARCODE_TYPES = [
    ('ean13', 'EAN13'),
    ('dun14', 'DUN14'),
]


class ProductProduct(models.Model):
    _inherit = 'product.product'

    quality_check_ids = fields.Many2many(
        'product.quality.check',
        rel='product_quality_check_product_rel',
        id1='product_id', id2='quality_id'
    )


class ProductQualityCheck(models.Model):
    _name = 'product.quality.check'
    _order = 'quality_type desc, sequence, id'

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    product_ids = fields.Many2many(
        'product.product',
        rel='product_quality_check_product_rel',
        id1='quality_id', id2='product_id'
    )
    quality_type = fields.Selection(QUALITY_TYPES, 'Control Type')
    value_type = fields.Selection(VALUE_TYPES, 'Value Type')
    workcenter_id = fields.Many2one(
        'mrp.workcenter', 'Work Center', readonly=False)
    repeat = fields.Integer('Repeat each')
    required_text = fields.Char('Required Text')
    min_value = fields.Float('Minimum Value')
    max_value = fields.Float('Maximum Value')
    barcode_type = fields.Selection(BARCODE_TYPES, 'Barcode Type')
