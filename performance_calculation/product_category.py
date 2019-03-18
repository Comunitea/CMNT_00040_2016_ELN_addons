# -*- coding: utf-8 -*-
# Copyright 2019 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    applies_overweight_calculation = fields.Boolean(
        string='Applies in overweight calculation',
        help='If checked, products in this category will be considered '
             'in the calculation of overweight for productions.')
