# -*- coding: utf-8 -*-
# Copyright 2017 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields
from datetime import datetime


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    lead_time = fields.Float(string='Lead time (h)',
        compute='_get_indicators',
        readonly=True)
    overweight = fields.Float(string='Overweight (%)',
        compute='_get_indicators',
        readonly=True)
    theorical_overweight = fields.Float(string='Theo. Overweight (%)',
        readonly=True)
    ind_scrap = fields.Float(string='Indicator Scrap',
        compute='_get_indicators',
        readonly=True)
    ind_usage = fields.Float(string='Indicator Usage',
        compute='_get_indicators',
        readonly=True)

    @api.multi
    def _get_indicators(self):
        pc_obj = self.env['performance.calculation']
        for production in self:
            lead_time = overweight = scrap = usage = 0.0
            if production.state == 'done':
                # lead time
                create_date = datetime.strptime(production.date, '%Y-%m-%d %H:%M:%S')
                wl_date_finished = production.workcenter_lines.mapped('date_finished') or [production.date_finished]
                date_finished = wl_date_finished and all(wl_date_finished) and datetime.strptime(max(wl_date_finished), '%Y-%m-%d %H:%M:%S')
                if create_date and date_finished:
                    lead_time = date_finished and (date_finished - create_date)
                    lead_time = lead_time and round(lead_time.total_seconds() / 3600, 2)
                # overweight
                result = pc_obj._get_overweight(production)
                overweight = result['overweight']
                # scrap & usage
                result = pc_obj._get_scrap_and_usage(production)
                scrap = result['scrap']
                usage = result['usage']
            production.lead_time = lead_time
            production.overweight = overweight
            production.ind_scrap = scrap
            production.ind_usage = usage

    @api.multi
    def action_confirm(self):
        pc_obj = self.env['performance.calculation']
        res = super(MrpProduction, self).action_confirm()
        for production in self:
            production.theorical_overweight = \
                pc_obj._get_theorical_overweight(production)
        return res


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    availability = fields.Float(string='Availability',
        compute='_get_indicators',
        readonly=True)
    performance = fields.Float(string='Performance',
        compute='_get_indicators',
        readonly=True)
    quality = fields.Float(string='Quality',
        compute='_get_indicators',
        readonly=True)
    oee = fields.Float(string='OEE',
        compute='_get_indicators',
        readonly=True)

    @api.multi
    def _get_indicators(self):
        pc_obj = self.env['performance.calculation']
        for wl in self:
            availability = performance = quality = oee = 0.0
            if wl.state == 'done':
                availability, performance, quality, oee = pc_obj._get_oee(wl)
            wl.availability = availability
            wl.performance = performance
            wl.quality = quality
            wl.oee = oee
