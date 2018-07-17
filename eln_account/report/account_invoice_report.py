# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp import tools
import openerp.addons.decimal_precision as dp
from openerp.osv import fields,osv

class account_invoice_report(osv.osv):
    _inherit = "account.invoice.report"

    _columns = {
        'number': fields.char('Number', readonly=True),
        'cost_total': fields.float('Total Cost', readonly=True),
        'benefit_total': fields.float('Total Benefit', readonly=True),
        'format_id': fields.many2one('product.format', 'Format', readonly=True),
        'trademark_id': fields.many2one('product.trademark', 'Trademark', readonly=True),
        'weight_net': fields.float('Net Weight', readonly=True, help="The net weight in Kg."),
    }
    
    _depends = {
        'account.invoice': ['number'],
        'account.invoice.line': ['cost_subtotal'],
    }

    def _select(self):
        select_str = """
        , sub.number, sub.cost_total, sub.price_total - sub.cost_total as benefit_total,
        sub.format_id, sub.trademark_id, sub.weight_net * sub.product_qty as weight_net
        """
        return super(account_invoice_report, self)._select() + select_str

    def _sub_select(self):
        select_str = """
        , ai.number,
        SUM(CASE
             WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                THEN - ail.cost_subtotal
                ELSE ail.cost_subtotal
            END) AS cost_total,
        pt.format_id, pt.trademark_id, pt.weight_net
        """
        return super(account_invoice_report, self)._sub_select() + select_str

    def _group_by(self):
        group_by_str = """
        , ai.number, pt.format_id, pt.trademark_id, pt.weight_net
        """
        return super(account_invoice_report, self)._group_by() + group_by_str

