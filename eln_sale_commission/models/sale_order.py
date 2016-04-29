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
        t_partner = self.env['res.partner']
        if self.env.context.get('partner_id'):
            partner_id = self.env.context['partner_id']
            ship_address_id = self.env.context.get('address_id', False)
            ship_address = t_partner.browse(ship_address_id)
            if ship_address_id and ship_address_id != partner_id and \
                    ship_address.commission_ids:
                sol = self.with_context(partner_id=self._context['address_id'])
                return super(SaleOrderLine, sol)._default_agents()
        return super(SaleOrderLine, self)._default_agents()

    agents = fields.One2many(default=_default_agents)


class SaleOrderLineAgent(models.Model):

    _inherit = 'sale.order.line.agent'

    _sql_constraints = [
        ('unique_agent', 'Check(1=1)',
         'You can only add one time each agent.!'),
    ]
