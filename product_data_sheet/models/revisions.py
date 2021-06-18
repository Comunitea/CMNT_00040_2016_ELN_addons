# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ProductRevision(models.Model):
    _name = 'product.revision'

    name = fields.Char('Name', size=64,
        required=True)
    product_technical_sheet_id = fields.Many2one(
        'product.technical.sheet', 'Technical sheet',
        required=True, ondelete='cascade')
    user_id = fields.Many2one(
        'res.users', 'User',
        default=lambda self: self.env.user)
    date = fields.Date('Date',
        default=lambda s: fields.Date.context_today(s))
    description = fields.Text('Description')
