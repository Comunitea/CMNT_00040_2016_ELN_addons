# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    quality_check_ids = fields.Many2many(
        'product.quality.check',
        rel='product_quality_check_product_rel',
        id1='product_id', id2='quality_id'
    )
    quality_checks_to_apply = fields.Selection([
        ('product', 'Product'),
        ('workcenter', 'Work Center'),
        ('all', 'All'),
        ], string='Quality checks to apply',
        default='all')
