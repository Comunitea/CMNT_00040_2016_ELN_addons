# -*- coding: utf-8 -*-
# Copyright 2023 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api

class L10nEsAeatMod303Report(models.Model):
    _inherit = "l10n.es.aeat.mod303.report"

    @api.multi
    @api.depends('tax_lines', 'tax_lines.amount')
    def _compute_total_devengado(self):
        casillas_devengado = (3, 6, 9, 11, 13, 15, 18, 21, 24, 26, 152, 155, 158, 167, 170)
        for report in self:
            tax_lines = report.tax_lines.filtered(
                lambda x: x.field_number in casillas_devengado)
            report.total_devengado = sum(tax_lines.mapped('amount'))

    @api.onchange('period_type', 'fiscalyear_id')
    def onchange_period_type(self):
        super(L10nEsAeatMod303Report, self).onchange_period_type()
        if (self.fiscalyear_id and
                self.fiscalyear_id.date_start >= '2023-01-01'):
            self.export_config = self.env.ref(
                'eln_l10n_es.'
                'aeat_mod303_2023_main_export_config')


class AeatModMapTaxCode(models.Model):
    _inherit = 'aeat.mod.map.tax.code'

    @api.one
    @api.constrains('date_from', 'date_to')
    def _unique_date_range(self):
        return True