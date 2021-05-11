# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api
from openerp.addons.quality_control.models.qc_trigger_line import _filter_trigger_lines


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def action_produce(self, production_id, production_qty, production_mode,
                       wiz=False):
        """"
        En eln_production se añade a production_mode el modo: 'produce'.
        No ponemos dicho módulo como dependencia ya que en caso de no estar instalado
        este código sería inocuo y no generaría tampoco ningún error.
        """
        production = self.browse(production_id)
        done_moves = production.move_created_ids2.filtered(
            lambda r: r.state == 'done')
        res = super(MrpProduction, self).action_produce(
            production_id, production_qty, production_mode, wiz=wiz)
        if production_mode == 'produce':
            inspection_model = self.env['qc.inspection']
            for move in production.move_created_ids2.filtered(
                    lambda r: r.state == 'done') - done_moves:
                qc_trigger = self.env.ref('quality_control_mrp.qc_trigger_mrp')
                trigger_lines = set()
                for model in ['qc.trigger.product_category_line',
                              'qc.trigger.product_template_line',
                              'qc.trigger.product_line']:
                    trigger_lines = trigger_lines.union(
                        self.env[model].get_trigger_line_for_product(
                            qc_trigger, move.product_id))
                for trigger_line in _filter_trigger_lines(trigger_lines):
                    inspection_model._make_inspection(move, trigger_line)
        return res
