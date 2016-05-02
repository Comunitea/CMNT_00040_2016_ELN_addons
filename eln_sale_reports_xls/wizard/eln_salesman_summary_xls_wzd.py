# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class ElnSaleSummaryXlsWzd(models.TransientModel):
    _name = 'eln.salesman.summary.xls.wzd'

    start_date = fields.Date('Start Date', required=True,
                             default=fields.Date.today())
    end_date = fields.Date('End Date', required=True,
                           default=fields.Date.today())

    @api.multi
    def get_pick_values(self, pick):
        cost = sale = 0.0
        for move in pick.move_lines:
            cost += move.product_id.standard_price * move.product_uom_qty
            sale += move.price_subtotal
        return cost, sale

    @api.multi
    def get_company_ids(self):
        res = []
        t_company = self.env['res.company'].sudo()
        objs = t_company.search([('parent_id', '!=', False)])
        res = [x.id for x in objs]
        return res

    @api.multi
    def _get_report_data(self):
        self.ensure_one()
        t_pick = self.env['stock.picking'].sudo()
        res = {}
        company_ids = self.get_company_ids()
        for c_id in company_ids:
            res[c_id] = {}
        domain = [
            ('picking_type_code', '=', 'outgoing'),
            ('state', 'not in', ['draft', 'cancel']),
            ('min_date', '>=', self.start_date),
            ('min_date', '<=', self.end_date),
            ('company_id', 'in', company_ids)
        ]
        for pick in t_pick.search(domain):
            c = pick.company_id.id
            if not pick.sale_id and pick.sale_id.user_id:
                continue
            user_id = pick.sale_id.user_id.id
            if user_id not in res:
                res[c][user_id] = {
                    'cost': 0.0,
                    'sale': 0.0,
                }

            cost, sale = self.get_pick_values(pick)
            res[c][user_id]['cost'] += cost
            res[c][user_id]['sale'] += sale

        return res

    @api.multi
    def create_xls_report(self):
        self.ensure_one()
        data = self._get_report_data()
        return {'type': 'ir.actions.report.xml',
                'report_name': 'eln_salesman_summary_xls',
                'datas': data}
