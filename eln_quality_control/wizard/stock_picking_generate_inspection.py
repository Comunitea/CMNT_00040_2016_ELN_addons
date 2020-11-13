# -*- coding: utf-8 -*-
# Copyright 2020 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, _
from openerp.addons.quality_control.models.qc_trigger_line import _filter_trigger_lines


class StockPickingQcInspectionWzd(models.TransientModel):
    _name = 'stock.picking.qc.inspection.wzd'

    @api.multi
    def generate_qc_inspection(self):
        self.ensure_one()
        picking_ids = self._context.get('active_ids', [])
        pickings = self.env['stock.picking'].browse(picking_ids)
        pickings = pickings.filtered(lambda r: r.state == 'done')
        inspection_model = inspections = self.env['qc.inspection']
        for picking in pickings:
            for operation in picking.pack_operation_ids:
                qc_trigger = self.env['qc.trigger'].search(
                    [('picking_type', '=', picking.picking_type_id.id)])
                trigger_lines = set()
                for model in ['qc.trigger.product_category_line',
                              'qc.trigger.product_template_line',
                              'qc.trigger.product_line']:
                    partner = (picking.partner_id
                               if qc_trigger.partner_selectable else False)
                    trigger_lines = trigger_lines.union(
                        self.env[model].get_trigger_line_for_product(
                            qc_trigger, operation.product_id, partner=partner))
                for trigger_line in _filter_trigger_lines(trigger_lines):
                    inspections |= inspection_model._make_inspection(operation, trigger_line)
        if inspections:
            inspections.write({'auto_generated': False})
        if len(pickings) > 1:
            domain = [('id', 'in', inspections._ids)]
        else:
            domain = [('picking', 'in', pickings._ids)]
            
        return {
            'domain': domain,
            'name': _('Quality inspections from picking'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'qc.inspection',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
