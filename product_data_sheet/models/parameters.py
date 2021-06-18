# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ProductParameter(models.Model):
    _name = 'product.parameter'

    name = fields.Char('Name', size=256,
        required=True, translate=True)
    type = fields.Selection([
        ('chemical', 'Chemical'),
        ('physical', 'Physical'),
        ('microbiological', 'Microbiological'),
        ('organoleptic', 'Organoleptic')
        ], string='Type', required=True)


class ProductParameterProduct(models.Model):
    _name = 'product.parameter.product'

    name = fields.Char('Name', size=64,
        required=True, default='/')
    product_technical_sheet_id = fields.Many2one(
        'product.technical.sheet', 'Technical sheet',
        required=True, ondelete='cascade')
    parameter_id = fields.Many2one(
        'product.parameter', 'Parameter')
    value = fields.Char('Value', size=128, translate=True)
