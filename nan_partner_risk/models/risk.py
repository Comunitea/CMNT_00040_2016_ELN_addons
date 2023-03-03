# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009 Albert Cervera i Areny (http://www.nan-tic.com). All Rights Reserved
#    Copyright (c) 2011 Pexego Sistemas Informáticos. All Rights Reserved
#                       Alberto Luengo Cabanillas <alberto@pexego.es>
#    Copyright (c) 2015 Comunitea Servicios Tecnológicos. All Rights Reserved
#                       Omar Castiñeira Saavedra <omar@comunitea.com>
#    Copyright (C) 2019 El Nogal - Pedro Gómez <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
import time


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[
        ('wait_risk', 'Waiting Risk Approval'),
        ('risk_approved', 'Risk Approved'),
    ])

    @api.multi
    def onchange_partner_id(self, part):
        res = super(SaleOrder, self).onchange_partner_id(part)
        if part and not self._context.get('no_check_risk', False):
            partner = self.env['res.partner'].browse(part).commercial_partner_id
            if partner.credit_limit and partner.available_risk < 0.0:
                res['warning'] = {
                    'title': _('Credit Limit Exceeded'),
                    'message': _('Warning: Credit Limit Exceeded.\n\nThis partner has a credit limit of %(limit).2f and already has a debt of %(debt).2f.') % {
                        'limit': partner.credit_limit,
                        'debt': partner.total_debt,
                    }
                }
        return res

    @api.multi
    def test_risk(self):
        """ Hace un test de riesgo para un determinado pedido de venta.
        @return: True : ha pasado el test
                False : no ha pasado el test
        """
        res = True
        for order in self:
            partner_id = order.partner_id.commercial_partner_id
            if not partner_id.risk_insurance_status:
                res = True
            else:
                if order.order_policy == 'no_bill':
                    res = partner_id.risk_insurance_status not in ('denied', 'incidents')
                else:
                    if partner_id.risk_insurance_status not in ('company_granted', 'insurance_granted'):
                        res = False
                    else:
                        res = (partner_id.available_risk - order.amount_total) >= 0.0
        return res


class ResPartner(models.Model):
    _inherit = 'res.partner'

    unpayed_amount = fields.Float('Expired Unpaid Payments', compute='_unpayed_amount')
    pending_amount = fields.Float('Unexpired Pending Payments', compute='_pending_amount')
    draft_invoices_amount = fields.Float('Draft Invoices', compute='_draft_invoices_amount')
    pending_orders_amount = fields.Float('Uninvoiced Orders', compute='_pending_orders_amount')
    total_debt = fields.Float('Total Debt', compute='_total_debt')
    available_risk = fields.Float('Available Credit', compute='_available_risk')
    total_risk_percent = fields.Float('Credit Usage (%)', compute='_total_risk_percent')

    @api.multi
    def _unpayed_amount(self):
        t_aml = self.env['account.move.line']
        today = time.strftime('%Y-%m-%d')
        for partner in self:
            accounts = []
            if partner.company_id.individual_risk_check:
                extra_domain = []
                if partner.property_account_receivable:
                    accounts.append(partner.property_account_receivable.id)
                if partner.property_account_payable:
                    accounts.append(partner.property_account_payable.id)
            else:
                company_ids = partner.sudo().company_id + partner.sudo().company_id.child_ids
                extra_domain = [('company_id', 'in', company_ids._ids)]
                t_aml = t_aml.sudo()
                for company_id in company_ids:
                    s_partner =  partner.sudo().with_context(force_company=company_id.id)
                    if s_partner.property_account_receivable:
                        accounts.append(s_partner.property_account_receivable.id)
                    if s_partner.property_account_payable:
                        accounts.append(s_partner.property_account_payable.id)
            domain = [
                ('partner_id', '=', partner.id),
                ('account_id', 'in', accounts),
                ('reconcile_id', '=', False),
                ('date_maturity', '<', today)
            ] + extra_domain
            line_ids = t_aml.search(domain)
            # Those that have amount_residual == 0, will mean that they're circulating. The payment request has been sent
            # to the bank but have not yet been reconciled (or the date_maturity has not been reached).
            amount = 0.0
            for line in line_ids:
                if line.currency_id:
                    sign = line.amount_currency < 0 and -1 or 1
                else:
                    sign = (line.debit - line.credit) < 0 and -1 or 1
                if line.reconcile_partial_id:
                    amount += line.debit - line.credit
                else:
                    amount += sign * line.amount_residual
            partner.unpayed_amount = amount

    @api.multi
    def _pending_amount(self):
        t_aml = self.env['account.move.line']
        today = time.strftime('%Y-%m-%d')
        for partner in self:
            accounts = []
            if partner.company_id.individual_risk_check:
                extra_domain = []
                if partner.property_account_receivable:
                    accounts.append(partner.property_account_receivable.id)
                if partner.property_account_payable:
                    accounts.append(partner.property_account_payable.id)
            else:
                company_ids = partner.sudo().company_id + partner.sudo().company_id.child_ids
                extra_domain = [('company_id', 'in', company_ids._ids)]
                t_aml = t_aml.sudo()
                for company_id in company_ids:
                    s_partner =  partner.sudo().with_context(force_company=company_id.id)
                    if s_partner.property_account_receivable:
                        accounts.append(s_partner.property_account_receivable.id)
                    if s_partner.property_account_payable:
                        accounts.append(s_partner.property_account_payable.id)
            domain = [
                ('partner_id', '=', partner.id),
                ('account_id', 'in', accounts),
                ('reconcile_id', '=', False),
                '|', ('date_maturity', '>=', today), ('date_maturity', '=', False)
            ] + extra_domain
            line_ids = t_aml.search(domain)
            # Those that have amount_residual == 0, will mean that they're circulating. The payment request has been sent
            # to the bank but have not yet been reconciled (or the date_maturity has not been reached).
            amount = 0.0
            for line in line_ids:
                if line.currency_id:
                    sign = line.amount_currency < 0 and -1 or 1
                else:
                    sign = (line.debit - line.credit) < 0 and -1 or 1
                if line.reconcile_partial_id:
                    amount += line.debit - line.credit
                else:
                    amount += sign * line.amount_residual
            partner.pending_amount = amount

    @api.multi
    def _draft_invoices_amount(self):
        t_ai = self.env['account.invoice']
        today = time.strftime('%Y-%m-%d')
        for partner in self:
            if partner.company_id.individual_risk_check:
                extra_domain = []
            else:
                company_ids = partner.sudo().company_id + partner.sudo().company_id.child_ids
                extra_domain = [('company_id', 'in', company_ids._ids)]
                t_ai = t_ai.sudo()
            domain = [
                ('partner_id', 'child_of', [partner.id]),
                ('state', '=', 'draft'),
                '|', ('date_due', '>=', today), ('date_due', '=', False)
            ] + extra_domain
            invids = t_ai.search(domain)
            val = 0.0
            for invoice in invids:
                # Note that even if the invoice is in 'draft' state it can have an account.move because it
                # may have been validated and brought back to draft. Here we'll only consider invoices with
                # NO account.move as those will be added in other fields.
                if invoice.move_id:
                    continue
                if invoice.type in ('out_invoice', 'in_refund'):
                    val += invoice.amount_total
                else:
                    val -= invoice.amount_total
            partner.draft_invoices_amount = val

    @api.multi
    def _pending_orders_amount(self):
        t_sm = self.env['stock.move']
        t_sol = self.env['sale.order.line']
        for partner in self:
            total = 0.0
            if partner.company_id.individual_risk_check:
                extra_domain = []
            else:
                company_ids = partner.sudo().company_id + partner.sudo().company_id.child_ids
                extra_domain = [('company_id', 'in', company_ids._ids)]
                t_sm = t_sm.sudo()
                t_sol = t_sol.sudo()
            domain = [
                ('partner_id', 'child_of', [partner.id]),
                ('state', 'not in', ['draft', 'cancel']),
                ('procurement_id', '!=', False),
                ('location_id.usage', '!=', 'transit'), # La regla de seguridad (custom) de stock_move no filtra esta ubicación por compañía.
                ('invoice_state', '=', '2binvoiced')
            ] + extra_domain
            mids = t_sm.search(domain)
            for move in mids.filtered(
                  lambda r: r.procurement_id.sale_line_id != False): # Se filtra aquí en lugar de en el search porque es más rápido.
                line = move.procurement_id.sale_line_id
                sign = move.picking_id.picking_type_code == "outgoing" and 1 or -1
                line_amount_total = line.tax_id.compute_all(
                    line.price_unit * (1-(line.discount or 0.0)/100.0),
                    move.product_uom_qty, product=line.product_id.id,
                    partner=line.order_partner_id.commercial_partner_id.id)['total_included']
                total += sign * line_amount_total
            domain = [
                ('order_partner_id', 'child_of', [partner.id]),
                ('state', 'not in', ['draft', 'cancel']),
                ('invoiced', '=', False),
                '|', ('product_id', '=', False),
                ('product_id.type', '=', 'service')
            ] + extra_domain
            sids = t_sol.search(domain)
            for sline in sids:
                line_amount_total = sline.tax_id.compute_all(
                    sline.price_unit * (1-(sline.discount or 0.0)/100.0),
                    sline.product_uom_qty, product=sline.product_id.id,
                    partner=sline.order_partner_id.commercial_partner_id.id)['total_included']
                total += line_amount_total
            partner.pending_orders_amount = total

    @api.multi
    def _total_debt(self):
        for partner in self:
            pending_orders = partner.pending_orders_amount or 0.0
            unpayed = partner.unpayed_amount or 0.0
            pending = partner.pending_amount or 0.0
            draft_invoices = partner.draft_invoices_amount or 0.0
            partner.total_debt = pending_orders + unpayed + pending + draft_invoices

    @api.multi
    def _available_risk(self):
        for partner in self:
            partner.available_risk = partner.credit_limit - partner.total_debt

    @api.multi
    def _total_risk_percent(self):
        for partner in self:
            if partner.credit_limit:
                total_risk_percent = 100.0 * partner.total_debt / partner.credit_limit
            else:
                total_risk_percent = 100
            partner.total_risk_percent = total_risk_percent


class ResCompany(models.Model):
    _inherit = "res.company"

    individual_risk_check = fields.Boolean(
       string='Individual risk check',
       default=True,
       help="If checked, the risk control will use the user's company for the calculations. "
            "Otherwise, the company of the partner and childs will be used for the calculations."
    )

