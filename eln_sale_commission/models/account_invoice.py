# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    _sql_constraints = [
        ('unique_agent', 'Check(1=1)',
         'You can only add one time each agent.')
    ]
