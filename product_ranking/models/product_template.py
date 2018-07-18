# -*- coding: utf-8 -*-
# Copyright 2018 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    ranking1_id = fields.Many2one(string="Ranking 1", comodel_name='product.ranking')
    ranking2_id = fields.Many2one(string="Ranking 2", comodel_name='product.ranking')
