# -*- coding: utf-8 -*-
# Copyright 2022 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    tag_ids = fields.Many2many(
        'product.tags', string='Tags',
        rel='product_tags_product_template_rel',
        id1='tag_id', id2='product_id'
    )

