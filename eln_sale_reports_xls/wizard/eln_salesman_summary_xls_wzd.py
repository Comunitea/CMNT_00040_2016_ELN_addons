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
        c = self._context.copy()
        user_company_id = self.env['res.users'].browse(self._uid).company_id.id
        company_id = pick.company_id.id
        c.update(company_id=company_id,
                 force_company=company_id)
        t_product = self.env['product.product'].with_context(c)
        if company_id != user_company_id:
            t_product = self.env['product.product'].sudo().with_context(c)
        for move in pick.move_lines:
            product = t_product.browse(move.product_id.id)
            standard_price = product.standard_price
            cost += standard_price * move.product_uom_qty
            sale += move.price_subtotal
        return cost, sale

    @api.multi
    def _get_report_data(self):
        valquin_id = 2
        quival_id = 3
        self.ensure_one()
        t_pick = self.env['stock.picking'].sudo()
        res = {}
        domain = [
            ('picking_type_code', '=', 'outgoing'),
            ('state', 'not in', ['draft', 'cancel']),
            ('min_date', '>=', self.start_date),
            ('min_date', '<=', self.end_date),
            ('company_id', 'in', [valquin_id, quival_id])
        ]
        for pick in t_pick.search(domain):

            # Get company mode
            c = 'valquin'
            if pick.company_id.id == valquin_id and not pick.supplier_id:
                c = 'valquin'
            elif pick.company_id.id == valquin_id and pick.supplier_id:
                c = 'indir_valquin'
            elif pick.company_id.id == quival_id:
                c = 'quival'

            # Group by salesman
            com = 'Desconocido'
            if pick.sale_id and pick.sale_id.user_id:
                com = pick.sale_id.user_id.name
            if com not in res:
                res[com] = {c: {'cost': 0.0, 'sale': 0.0}}
            elif c not in res[com]:
                res[com][c] = {'cost': 0.0, 'sale': 0.0}

            cost, sale = self.get_pick_values(pick)
            res[com][c]['cost'] += cost
            res[com][c]['sale'] += sale
        return res

    @api.multi
    def create_xls_report(self):
        self.ensure_one()
        data = self._get_report_data()
        return {'type': 'ir.actions.report.xml',
                'report_name': 'eln_salesman_summary_xls',
                'datas': data}
