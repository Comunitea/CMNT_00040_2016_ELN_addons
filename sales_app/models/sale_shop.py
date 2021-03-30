# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class SaleShop(models.Model):
    _inherit = 'sale.shop'

    in_app = fields.Boolean('Show in APP', default=False)
