# -*- coding: utf-8 -*-
# Copyright 2020 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, _
from openerp.addons.quality_control.models.qc_trigger_line import _filter_trigger_lines


class MrpProductionQcInspectionWzd(models.TransientModel):
    _name = 'mrp.production.qc.inspection.wzd'

    @api.multi
    def generate_qc_inspection(self):
        self.ensure_one()
        production_ids = self._context.get('active_ids', [])
        productions = self.env['mrp.production'].browse(production_ids)
        productions = productions.filtered(lambda r: r.state not in ('draft', 'cancel'))
        inspection_model = inspections = self.env['qc.inspection']
        for production in productions:
            inspection_model = self.env['qc.inspection']
            for move in production.move_created_ids2.filtered(
                    lambda r: r.state == 'done'):
                qc_triggers = \
                    self.env.ref('quality_control_mrp.qc_trigger_mrp') + \
                    self.env.ref('eln_quality_control.qc_trigger_mrp_manual')
                for qc_trigger in qc_triggers:
                    trigger_lines = set()
                    for model in ['qc.trigger.product_category_line',
                                  'qc.trigger.product_template_line',
                                  'qc.trigger.product_line']:
                        trigger_lines = trigger_lines.union(
                            self.env[model].get_trigger_line_for_product(
                                qc_trigger, move.product_id))
                    for trigger_line in _filter_trigger_lines(trigger_lines):
                        inspections |= inspection_model._make_inspection(move, trigger_line)
        if inspections:
            inspections.write({'auto_generated': False})
        if len(productions) > 1:
            domain = [('id', 'in', inspections._ids)]
        else:
            domain = [('production', 'in', productions._ids)]
            
        return {
            'domain': domain,
            'name': _('Quality inspections from productions'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'qc.inspection',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
