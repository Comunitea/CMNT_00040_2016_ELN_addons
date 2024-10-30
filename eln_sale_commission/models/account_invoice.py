# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def _default_agents(self):
        """
        Check if there are agents and commissions
        for the partner of the invoice.
        Otherwise, the commercial_partner_id will be used as reference.
        """
        t_partner = self.env['res.partner']
        if self.env.context.get('partner_id'):
            partner = t_partner.browse(self.env.context['partner_id'])
            if not partner.commission_ids:
                ail = self.with_context(
                        partner_id=partner.commercial_partner_id.id)
                return super(AccountInvoiceLine, ail)._default_agents()
        return super(AccountInvoiceLine, self)._default_agents()

    agents = fields.One2many(default=_default_agents)


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    invoiced_amount = fields.Float(
        string="Invoiced amount", compute="_compute_amount", store=True)

    def _compute_amount(self):
        super(AccountInvoiceLineAgent, self)._compute_amount()
        for line in self:
            line.invoiced_amount = line.invoice_line.price_subtotal
            if line.invoice.type in ('out_refund', 'in_refund'):
                line.invoiced_amount = -line.invoiced_amount
