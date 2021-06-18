# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_technical_sheet_ids = fields.One2many(
        'product.technical.sheet', 'product_id', 'Technical sheets')
    product_logistic_sheet_ids = fields.One2many(
        'product.logistic.sheet', 'product_id', 'Logistic sheets')
