# -*- coding: utf-8 -*-
# Copyright 2023 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    stock_move_id = fields.Many2one(select=True) # Redefine index
