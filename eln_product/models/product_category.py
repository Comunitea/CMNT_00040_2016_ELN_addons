# -*- coding: utf-8 -*-
# Copyright 2022 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


EXPECTED_USE_TYPES = [
    ('raw', 'Raw materials'),
    ('auxiliary', 'Auxiliary materials'),
    ('packaging', 'Packaging materials'),
    ('semifinished', 'Semi-finished goods'),
    ('finished', 'Finished goods')
]


class ProductCategory(models.Model):
    _inherit = 'product.category'

    expected_use = fields.Selection(EXPECTED_USE_TYPES, 'Expected use')
    recursively_expected_use = fields.Selection(EXPECTED_USE_TYPES, 'Recursively expected use',
        compute='_get_recursively_expected_use')

    @api.multi
    def _get_recursively_expected_use(self):
        for categ in self:
            expected_use = categ.expected_use
            parent_categ = categ.parent_id
            while parent_categ and not expected_use:
                expected_use = parent_categ.expected_use
                parent_categ = parent_categ.parent_id
            categ.recursively_expected_use = expected_use

