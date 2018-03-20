# -*- coding: utf-8 -*-
# Copyright 2017 Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class SaleReport(models.Model):
    _inherit = "sale.report"

    effective_date = fields.Date(string='Effective Date', readonly=True)

    def _select(self):
        return super(SaleReport, self)._select() + ", s.effective_date"

    def _group_by(self):
        return super(SaleReport, self)._group_by() + ", s.effective_date"
