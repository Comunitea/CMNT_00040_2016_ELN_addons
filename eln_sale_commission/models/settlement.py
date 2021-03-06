# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Comunitea All Rights Reserved
#    $Jesús Ventosinos Mayor <jesus@comunitea.com>$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from datetime import datetime


class Settlement(models.Model):
    _inherit = "sale.commission.settlement"

    name = fields.Char('Name', compute='_get_name')

    @api.depends('lines', 'lines.settled_amount')
    def _compute_total(self):
        for record in self:
            record.total = \
                sum(((1 -
                    (x.invoice.partner_id.commercial_partner_id.atypical /
                        100)) * x.settled_amount) for x in record.lines)

    @api.multi
    def _get_name(self):
        for settlement_id in self:
            date_from = settlement_id.date_from and datetime.strptime(settlement_id.date_from, "%Y-%m-%d").strftime('%d-%m-%Y')
            date_to = settlement_id.date_to and datetime.strptime(settlement_id.date_to, "%Y-%m-%d").strftime('%d-%m-%Y')
            settlement_id.name = _("%s (from: %s, to: %s)") % (settlement_id.agent.name or '', date_from or '', date_to or '')


class SettlementLine(models.Model):
    _inherit = "sale.commission.settlement.line"

    @api.depends('invoice_line', 'partner_id')
    def _get_partner_shipping_id(self):
        for rec in self:
            partner = rec.invoice.partner_id
            if rec.invoice_line.stock_move_id:
                sm_partner = rec.invoice_line.stock_move_id.picking_id.partner_id
                if sm_partner.commercial_partner_id == partner.commercial_partner_id:
                    partner = sm_partner
            if partner:
                rec.partner_shipping_id = partner

    partner_id = fields.Many2one(
        comodel_name="res.partner", related="invoice.commercial_partner_id",
        store=True)
    partner_shipping_id = fields.Many2one('res.partner', string="Shipping Address",
                                 compute="_get_partner_shipping_id", readonly=True,
                                 store=True)
    commission = fields.Many2one(
        comodel_name="sale.commission", related="agent_line.commission",
        store=True)
    invoiced_amount = fields.Float(related="agent_line.invoiced_amount", store=True)
    atypical = fields.Float('Atypical', group_operator='avg', readonly=True)
    total_atypical = fields.Float('Total without atypical', readonly=True)
    date_from = fields.Date(related="settlement.date_from", string="From", store=True)
    date_to = fields.Date(related="settlement.date_to", string="To", store=True)
    user_id = fields.Many2one(
        comodel_name="res.users", related="agent_line.invoice_line.invoice_id.user_id",
        store=True)


class SaleCommissionMakeSettle(models.TransientModel):
    _inherit = "sale.commission.make.settle"

    @api.multi
    def action_settle(self):
        res = super(SaleCommissionMakeSettle, self).action_settle()
        if 'domain' not in res:
            return res  # Action window close
        settlement_ids = res['domain'][0][2]
        t_settle = self.env['sale.commission.settlement']
        for settle in t_settle.browse(settlement_ids):
            line_vals = []
            for l in settle.lines:
                atypical = l.invoice.partner_id.commercial_partner_id.atypical
                total_atypical = l.settled_amount * (1 - (atypical / 100))
                vals = {'settlement': settle.id,
                        'atypical': atypical,
                        'total_atypical': total_atypical}
                line_vals.append([l.id, vals])
            settle.write({'lines': [(1, x, y) for x, y in line_vals]})
        return res
