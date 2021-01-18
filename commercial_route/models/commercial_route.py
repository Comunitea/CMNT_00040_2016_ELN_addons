# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class CommercialRoute(models.Model):
    _name = 'commercial.route'
    _description = 'Commercial route'
    _order = 'sequence, code'

    code = fields.Char('Code', size=32)
    name = fields.Char('Name', size=255)
    user_id = fields.Many2one('res.users', 'Salesperson')
    sequence = fields.Integer('Sequence', default=1)
    partner_ids = fields.One2many(
        'res.partner', 'commercial_route_id', 'Partners',
        readonly=True)
