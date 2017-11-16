# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class ElnSaleReportXlsWzd(models.TransientModel):
    _name = 'eln.sale.report.xls.wzd'

    date = fields.Date('Report Date', required=True,
                       default=fields.Date.today())

    @api.multi
    def get_pick_values(self, pick):
        base = pur_price = kg = 0.0
        c = self._context.copy()
        company_id = pick.company_id.id
        user_company_id = self.env['res.users'].browse(self._uid).company_id.id
        c.update(company_id=company_id,
                 force_company=company_id)
        t_product = self.env['product.product'].with_context(c)
        if company_id != user_company_id:
            t_product = self.env['product.product'].sudo().with_context(c)
        for move in pick.move_lines:
            product = t_product.browse(move.product_id.id)
            standard_price = product.standard_price
            kg += move.product_id.weight_net * move.product_uom_qty
            pur_price += standard_price * move.product_uom_qty
            base += move.price_subtotal
        return base, pur_price, kg

    @api.multi
    def _get_report_data(self):
        self.ensure_one()
        t_pick = self.env['stock.picking']
        res = {}
        y, m, d = self.date.split('-')
        init_date = '-'.join([y, m, '0' + str(1)])
        end_date = self.date
        last_y = str(int(y) - 1)
        ly_init_date = '-'.join([last_y, m, '0' + str(1)])
        ly_end_date = '-'.join([last_y, m, d])
        domain = [
            ('picking_type_code', '=', 'outgoing'),
            ('invoice_state', '!=', 'none'),
            ('state', 'not in', ['draft', 'cancel']),
            '|',
            '&',
            ('effective_date', '>=', init_date),
            ('effective_date', '<=', end_date),
            '&',
            ('effective_date', '>=', ly_init_date),
            ('effective_date', '<=', ly_end_date),
        ]
        for pick in t_pick.search(domain):
            sale_id = pick.sale_id
            if not sale_id:
                continue
            acc = sale_id.project_id
            if acc not in res:
                res[acc] = {
                    'base': 0.0,
                    'p_price': 0.0,
                    'kg': 0.0,
                    'ld_base': 0.0,  # last day
                    'ld_p_price': 0.0,
                    'ld_kg': 0.0,
                    'ly_base': 0.0,  # last year
                    'ly_p_price': 0.0,
                    'ly_kg': 0.0,
                    'quot1': 0.0,  # Not used yet
                    'quot2': 0.0  # Not used yet
                }

            base, pur_price, kg = self.get_pick_values(pick)
            # From init to Current days values
            if pick.effective_date >= init_date and pick.effective_date <= end_date:
                res[acc]['base'] += base
                res[acc]['p_price'] += pur_price
                res[acc]['kg'] += kg
            # From init to previous day of end date
            if pick.effective_date >= init_date and pick.effective_date < end_date:
                res[acc]['ld_base'] += base
                res[acc]['ld_p_price'] += pur_price
                res[acc]['ld_kg'] += kg
            # Last Year
            if pick.effective_date >= ly_init_date and pick.effective_date <= ly_end_date:
                res[acc]['ly_base'] += base
                res[acc]['ly_p_price'] += pur_price
                res[acc]['ly_kg'] += kg
        return res

    @api.multi
    def create_xls_report(self):
        self.ensure_one()
        res = self._get_report_data()
        data = {}
        for acc in res:
            data[acc.name] = res[acc]
        return {'type': 'ir.actions.report.xml',
                'report_name': 'eln_sale_report_xls',
                'datas': data}
