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
        for move in pick.move_lines:
            kg += move.product_id.weight_net * move.product_uom_qty
            pur_price += move.product_id.standard_price * move.product_uom_qty
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
            ('state', 'not in', ['draft', 'cancel']),
            '|',
            '&',
            ('min_date', '>=', init_date),
            ('min_date', '<=', end_date),
            '&',
            ('min_date', '>=', ly_init_date),
            ('min_date', '<=', ly_end_date),
        ]
        for pick in t_pick.search(domain):
            if not pick.sale_id:
                continue
            acc = pick.sale_id.project_id
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

            # From init to previous day of end date
            if pick.min_date >= init_date and pick.min_date != end_date:
                res[acc]['ld_base'] += base
                res[acc]['ld_p_price'] += pur_price
                res[acc]['ld_kg'] += kg
            # From init to Current days values
            if pick.min_date >= init_date and pick.min_date <= end_date:
                res[acc]['base'] += base
                res[acc]['p_price'] += pur_price
                res[acc]['kg'] += kg
            # Last Year
            if pick.min_date >= ly_init_date and pick.min_date <= ly_end_date:
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
