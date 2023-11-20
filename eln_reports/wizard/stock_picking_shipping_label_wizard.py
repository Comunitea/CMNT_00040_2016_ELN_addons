# -*- coding: utf-8 -*-
# Copyright 2022 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields, exceptions, _


class StockPickingShippingLabelWizard(models.TransientModel):
    _name = 'stock.picking.shipping.label.wizard'

    line_ids = fields.One2many(
        'stock.picking.shipping.label.wizard.line', 'wiz_id', 'Lines')

    @api.model
    def default_get(self, fields):
        res = super(StockPickingShippingLabelWizard, self).default_get(fields)
        active_model = self._context.get('active_model', False)
        active_ids = self._context.get('active_ids', [])
        lines = []
        if active_model == 'stock.picking':
            picking_ids = self.env['stock.picking'].browse(active_ids)
            picking_ids = picking_ids.filtered(
                lambda r: (
                    r.picking_type_code != 'incoming' and
                    r.state not in ('cancel')
                )
            )
            for picking_id in picking_ids.sorted(key=lambda r: (r.id)):
                lines.append({
                    'picking_id': picking_id.id,
                    'picking_name': picking_id.name,
                    'partner_shipping_id': picking_id.partner_id.display_name,
                    'total_packages': picking_id.transport_company_pallets or 1,
                    'note': picking_id.note,
                })
        res.update(line_ids=lines)
        return res

    @api.multi
    def print_report(self):
        line_ids = self.mapped('line_ids.id')
        if not line_ids:
            raise exceptions.Warning(_('Error'),
                _('Nothing to print'))
        custom_data = {'line_ids': line_ids}
        rep_name = 'stock_picking_shipping_label_wizard.stock_picking_shipping_label_report'
        rep_action = self.env['report'].get_action(self, rep_name)
        rep_action['data'] = custom_data
        return rep_action


class StockPickingShippingLabelWizardLine(models.TransientModel):
    _name = 'stock.picking.shipping.label.wizard.line'

    wiz_id = fields.Many2one(
        'stock.picking.shipping.label.wizard', 'Wizard')
    picking_id = fields.Many2one(
        'stock.picking', 'Stock Picking', readonly=True)
    picking_name = fields.Char('Stock Picking', readonly=True) #Sólo por rendimiento al cargar vista
    partner_shipping_id = fields.Char('Delivery Address', readonly=True)
    total_packages = fields.Integer('Number of packages',
        default=1)
    note = fields.Text('Notes')


class StockPickingShippingLabelWizardParser(models.AbstractModel):
    _name = 'report.stock_picking_shipping_label_wizard.stock_picking_shipping_label_report'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report_name = 'eln_reports.stock_picking_shipping_label_report'
        if not data:
            raise exceptions.Warning(_('Error'),
                _('You must print it from a wizard'))
        docs = self.env['stock.picking.shipping.label.wizard.line'].browse(data['line_ids']).sorted(
              key=lambda r: (r.picking_id.id))
        docargs = {
            'doc_ids': [],
            'doc_model': 'stock.picking.shipping.label.wizard.line',
            'docs': docs,
        }
        return report_obj.render(report_name, docargs)
