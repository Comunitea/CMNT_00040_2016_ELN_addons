# -*- coding: utf-8 -*-
# Copyright 2022 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ProductTags(models.Model):
    _name = 'product.tags'

    name = fields.Char('Name', size=64, required=True)
    active = fields.Boolean('Active', default=True)

