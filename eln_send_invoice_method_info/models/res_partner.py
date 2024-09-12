# -*- coding: utf-8 -*-
# Copyright 2024 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class res_partner(models.Model):
    _inherit = 'res.partner'

    send_invoice_method = fields.Selection([
        ('paper', 'Paper'),
        ('email', 'Email'),
        ('edi', 'EDI'),
        ('paper_email', 'Paper & Email'),
        ('paper_edi', 'Paper & EDI'),
        ('email_edi', 'Email & EDI'),
        ], string="Send invoice method", default='')
