# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    commercial_route_id = fields.Many2one(
        string='Commercial route',
        comodel_name='commercial.route',
        domain="[('user_id', '=', user_id)]")
