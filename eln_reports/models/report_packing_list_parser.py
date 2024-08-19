# -*- coding: utf-8 -*-
# Copyright 2024 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class ReportPackingList(models.AbstractModel):
    _name = 'report.eln_reports.report_packing_list'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'eln_reports.report_packing_list')
        docs = []
        lang = data['form']['language'] or self.env.user.lang
        picking = self.env[report.model].with_context(lang=lang).browse(data['ids'])
        for picking in picking:
            docs.append(picking)
        docargs = {
            'doc_ids': data['ids'],
            'doc_model': report.model,
            'docs': docs,
            'data': data,
        }
        return report_obj.with_context(lang=lang).render(report.report_name, docargs)
