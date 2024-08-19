# -*- coding: utf-8 -*-
# Copyright 2024 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


def _lang_get(self):
    obj = self.env['res.lang']
    langs = obj.search([('translatable', '=', True)])
    res = [(lang.code, lang.name) for lang in langs]
    return res


class ReportPackingListWizard(models.TransientModel):
    _name = "report.packing.list.wizard"

    language = fields.Selection(_lang_get, 'Language',
        default=lambda self: self.env.user.lang,
        required=True)

    @api.multi
    def print_report(self):
        self.ensure_one()
        data = self.read()[0]
        data['active_ids'] = self._context.get('active_ids', [])
        datas = {
            'ids': self._context.get('active_ids', []),
            'model': 'stock.picking',
            'form': data,
        }
        return self.env['report'].get_action(self, 'eln_reports.report_packing_list', data=datas)
