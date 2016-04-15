# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    @api.model
    def _default_agents(self):
        """
        Check if there is a delivery address in the sale order and adds the
        agent and commission for this address if exists.
        """
        res = super(SaleOrderLine, self)._default_agents()

        res_extended = []
        if self.env.context.get('address_id'):
            sol = self.with_context(partner_id=self._context['address_id'])
            res_extended = super(SaleOrderLine, sol)._default_agents()

        res.extend(res_extended)
        return res

    agents = fields.One2many(default=_default_agents)
