# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class ElnSaleReportXlsWzd(models.TransientModel):
    _name = 'eln.sale.report.xls.wzd'

    date = fields.Date('Report Date', required=True,
                       default=fields.Date.today())

    @api.multi
    def create_xls_report(self):
        self.ensure_one()
        data = {'date': self.date}
        return {'type': 'ir.actions.report.xml',
                'report_name': 'eln_sale_report_xls',
                'datas': data}
