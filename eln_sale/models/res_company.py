# -*- coding: utf-8 -*-
# Copyright 2023 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    product_manufacturers_registry = fields.Char('Product manufacturers registry', 
        size=18, help="Product manufacturers registry. Format: ENV/Year of Registry/XXXXXXXXX")
