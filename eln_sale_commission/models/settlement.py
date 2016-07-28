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
from openerp import models, fields, api


class Settlement(models.Model):
    _inherit = "sale.commission.settlement"
    _rec_name = "agent"

    @api.depends('lines', 'lines.settled_amount')
    def _compute_total(self):
        for record in self:
            record.total = \
                sum(((1 -
                    (x.invoice.partner_id.commercial_partner_id.atypical /
                        100)) * x.settled_amount) for x in record.lines)


class SettlementLine(models.Model):
    _inherit = "sale.commission.settlement.line"

    @api.depends('invoice_line')
    def _get_partner_id(self):
        for rec in self:
            partner = False
            if rec.invoice_line:
                partner = rec.invoice_line.invoice_id.partner_id
                if rec.invoice_line.stock_move_id:
                    sm = rec.invoice_line.stock_move_id
                    if sm.picking_id and sm.picking_id.partner_id:
                        partner = sm.picking_id.partner_id
            if partner:
                rec.partner_id = partner.commercial_partner_id.id

    partner_id = fields.Many2one('res.partner', string="Partner",
                                 compute="_get_partner_id", readonly=True,
                                 store=True)
    commission = fields.Many2one(
        comodel_name="sale.commission", related="agent_line.commission",
        store=True)
    atypical = fields.Float('Atypical', group_operator='avg', readonly=True)
    total_atypical = fields.Float('Total with Atypical', readonly=True)


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
            for l in settle.lines:
                atypical = l.invoice.partner_id.commercial_partner_id.atypical
                total_atypical = l.settled_amount * (1 - (atypical / 100))
                l.write({'atypical': atypical,
                         'total_atypical': total_atypical})
        return res
