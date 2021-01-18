# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    commercial_route_id = fields.Many2one('commercial.route', 'Commercial route', readonly=True)

    def _select(self):
        select_str = """
        , sub.commercial_route_id
        """
        return super(AccountInvoiceReport, self)._select() + select_str

    def _sub_select(self):
        select_str = """
        , ai.commercial_route_id
        """
        return super(AccountInvoiceReport, self)._sub_select() + select_str

    def _group_by(self):
        group_by_str = """
        , ai.commercial_route_id
        """
        return super(AccountInvoiceReport, self)._group_by() + group_by_str

