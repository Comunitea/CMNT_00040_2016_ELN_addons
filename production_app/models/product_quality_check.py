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
    ('lot', 'Lot'),
]

BARCODE_TYPES = [
    ('ean13', 'EAN13'),
    ('dun14', 'DUN14'),
]


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
    workcenter_ids = fields.Many2many(
        'mrp.workcenter',
        rel='product_quality_check_workcenter_rel',
        id1='quality_id', id2='workcenter_id'
    )
    quality_type = fields.Selection(QUALITY_TYPES, 'Control Type')
    value_type = fields.Selection(VALUE_TYPES, 'Value Type')
    workcenter_id = fields.Many2one(
        'mrp.workcenter', 'Work Center', readonly=False,
        help="Restrict check to this Work Center")
    repeat = fields.Integer('Repeat each (minutes)')
    required_text = fields.Char('Required Text')
    min_value = fields.Float('Minimum Value')
    max_value = fields.Float('Maximum Value')
    barcode_type = fields.Selection(BARCODE_TYPES, 'Barcode Type')
    only_first_workorder = fields.Boolean('Only first time',
        help="Only first work order of the day for each Work Center")
    note = fields.Text('Notes')
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.user.company_id)
