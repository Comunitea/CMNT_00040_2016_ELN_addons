# -*- coding: utf-8 -*-
# Copyright 2026 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    origin_country_ids = fields.Many2many(
        'res.country', string='Country of origin',
        rel='product_template_origin_country_rel',
        id1='product_tmpl_id', id2='country_id'
    )
    variety = fields.Char('Variety')
