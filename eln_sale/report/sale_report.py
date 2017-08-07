# -*- coding: utf-8 -*-
# Copyright 2017 Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import tools
from openerp.osv import fields, osv

class sale_report(osv.osv):
    _inherit = "sale.report"

    _columns = {
        'effective_date': fields.date('Effective Date', readonly=True),
    }

    def _select(self):
        return super(sale_report, self)._select() + ", s.effective_date"

    def _group_by(self):
        return super(sale_report, self)._group_by() + ", s.effective_date"
