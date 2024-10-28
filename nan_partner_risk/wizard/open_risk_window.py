# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009 Albert Cervera i Areny (http://www.nan-tic.com). All Rights Reserved
#    Copyright (c) 2011 Pexego Sistemas Informáticos. All Rights Reserved
#                       Alberto Luengo Cabanillas <alberto@pexego.es>
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


""" Open Risk Window and show Partner relative information """

from odoo import models, fields, api, _


RISK_STATUS = [('company_granted', 'Credit granted by the company'),
               ('insurance_granted', 'Credit granted by the insurance'),
               ('requested', 'Insurance requested'),
               ('request_again', 'Insurance credit should be requested again'),
               ('denied', 'Credit denied by the insurance company'),
               ('incidents', 'Customer with incidents at risk'),
               ('new_customer', 'Warning! New customer - See payments')]

class OpenRiskWindow(models.TransientModel):
    """ Open Risk Window and show Partner relative information """
    _name = "open.risk.window"
    _description = "Partner's risk information"

    unpayed_amount = fields.Float('Expired Unpaid Payments', digits=(4, 2), readonly=True,
        default=lambda self: self.env['res.partner'].browse(self._context.get('risk_partner_id')).unpayed_amount or 0.0)
    pending_amount = fields.Float('Unexpired Pending Payments', digits=(4, 2), readonly=True,
        default=lambda self: self.env['res.partner'].browse(self._context.get('risk_partner_id')).pending_amount or 0.0)
    draft_invoices_amount = fields.Float('Draft Invoices', digits=(4, 2), readonly=True,
        default=lambda self: self.env['res.partner'].browse(self._context.get('risk_partner_id')).draft_invoices_amount or 0.0)
    pending_orders_amount = fields.Float('Uninvoiced Orders', digits=(4, 2), readonly=True,
        default=lambda self: self.env['res.partner'].browse(self._context.get('risk_partner_id')).pending_orders_amount or 0.0)
    total_debt = fields.Float('Total Debt', digits=(4, 2), readonly=True,
        default=lambda self: self.env['res.partner'].browse(self._context.get('risk_partner_id')).total_debt or 0.0)
    available_risk = fields.Float('Available Credit', digits=(4, 2), readonly=True,
        default=lambda self: self.env['res.partner'].browse(self._context.get('risk_partner_id')).available_risk or 0.0)
    total_risk_percent = fields.Float('Credit Usage (%)', digits=(4, 2), readonly=True,
        default=lambda self: self.env['res.partner'].browse(self._context.get('risk_partner_id')).total_risk_percent or 0.0)
    credit_limit = fields.Float('Credit Limit', digits=(4, 2), readonly=True,
        default=lambda self: self.env['res.partner'].browse(self._context.get('risk_partner_id')).credit_limit or 0.0)
    risk_insurance_status = fields.Selection(RISK_STATUS, string='Risk Status', readonly=True,
        help="This option is used to define the risk status.\n" \
        "Credit granted by the company: Only company's credit limit are applied.\n"\
        "Credit granted by the insurance: Only insurance's credit limit are applied.\n"\
        "Insurance requested: The risk has been requested to the insurance company.\n"\
        "Insurance credit should be requested again: The risk should be requested again to the insurance company.\n"\
        "Credit denied by the insurance company: The insurance company has denied the risk.\n"\
        "Customer with incidents at risk: The customer have incidents at risk.\n"\
        "Warning! New customer - See payments: New customer. Track payments.",
        default=lambda self: self.env['res.partner'].browse(self._context.get('risk_partner_id')).risk_insurance_status or '')
    risk_insurance_notes = fields.Text('Notes', readonly=True,
        default=lambda self: self.env['res.partner'].browse(self._context.get('risk_partner_id')).risk_insurance_notes or '')

    @api.model
    def default_get(self, fields):
        partner_obj = self.env['res.partner']
        if not self._context.get('risk_partner_id', False):  # Si no trae el parametro se supone que se llama desde el cliente
            partner_id = partner_obj.browse(self._context.get('active_id', False))
        else:
            partner_id = partner_obj.browse(self._context.get('risk_partner_id', False))
        self = self.with_context(risk_partner_id=partner_id.commercial_partner_id.id)
        res = super(OpenRiskWindow, self).default_get(fields)
        return res

