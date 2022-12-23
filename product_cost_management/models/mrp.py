# -*- coding: utf-8 -*-
# Copyright 2022 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models

class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    _order = 'sequence'
