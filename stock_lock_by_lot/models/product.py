# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    default_locked_lot = fields.Boolean(
        string='Lock new Serial Numbers/Lots',
        help='If checked, new Serial Numbers/lots will be created locked by default')
