# -*- coding: utf-8 -*-
# Copyright 2018 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields


class ProductRanking(models.Model):    
    _name = "product.ranking"
    _order = 'sequence'

    name = fields.Char('Name', size=64, required=True)
    sequence = fields.Integer('Sequence')
    type = fields.Selection([
        ('ranking1', 'Ranking 1'), 
        ('ranking2', 'Ranking 2')
        ], string="Type")
    active = fields.Boolean(
        string='Active',
        default=True)
