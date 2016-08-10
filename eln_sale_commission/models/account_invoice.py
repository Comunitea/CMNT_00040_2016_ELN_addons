# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    _sql_constraints = [
        ('unique_agent', 'Check(1=1)',
         'You can only add one time each agent.')
    ]

    invoiced_amount = fields.Float(
        string="Invoiced amount", compute="_compute_amount", store=True)

    def _compute_amount(self):
        super(AccountInvoiceLineAgent, self)._compute_amount()
        for line in self:
            line.invoiced_amount = line.invoice_line.price_subtotal
            if line.invoice.type in ('out_refund', 'in_refund'):
                line.invoiced_amount = -line.invoiced_amount
