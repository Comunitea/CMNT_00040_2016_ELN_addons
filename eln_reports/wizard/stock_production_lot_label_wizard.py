# -*- coding: utf-8 -*-
# Copyright 2022 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields, exceptions, _
from datetime import timedelta


class StockProductionLotLabelWizard(models.TransientModel):
    _name = 'stock.production.lot.label.wizard'

    line_ids = fields.One2many(
        'stock.production.lot.label.wizard.line', 'wiz_id', 'Lines')

    @api.model
    def default_get(self, fields):
        res = super(StockProductionLotLabelWizard, self).default_get(fields)
        active_model = self._context.get('active_model', False)
        active_ids = self._context.get('active_ids', [])
        lot_ids = False
        lines = []
        if active_model == 'stock.production.lot':
            lot_ids = self.env['stock.production.lot'].browse(active_ids)
            for lot_id in lot_ids:
                product_name = lot_id.product_id.name
                if lot_id.product_id.code:
                    product_name = '[%s] %s' % (lot_id.product_id.code, lot_id.product_id.name)
                lines.append({
                    'product_id': lot_id.product_id.id,
                    'lot_id': lot_id.id,
                    'partner_id': False,
                    'expected_use': lot_id.product_id.expected_use,
                    'product_name': product_name,
                    'lot_name': lot_id.name,
                    'use_date': lot_id.use_date,
                    'extended_shelf_life_date': lot_id.extended_shelf_life_date,
                    'partner_name': '',
                    'origin': '',
                })
        elif active_model == 'stock.picking':
            picking_ids = self.env['stock.picking'].browse(active_ids)
            for picking_id in picking_ids:
                if not picking_id.pack_operation_ids:
                    picking_id.do_prepare_partial()
                for op in picking_id.pack_operation_ids:
                    lot_id = op.lot_id.id
                    product_name = op.product_id.name
                    if op.product_id.code:
                        product_name = '[%s] %s' % (op.product_id.code, op.product_id.name)
                    lines.append({
                        'product_id': op.product_id.id,
                        'lot_id': op.lot_id.id,
                        'partner_id': picking_id.partner_id.id,
                        'expected_use': op.product_id.expected_use,
                        'product_name': product_name,
                        'lot_name': op.lot_id.name,
                        'use_date': op.lot_id.use_date,
                        'extended_shelf_life_date': op.lot_id.extended_shelf_life_date,
                        'partner_name': picking_id.partner_id.name,
                        'origin': '',
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
        rep_name = 'stock_production_lot_label_wizard.stock_production_lot_label_report'
        rep_action = self.env['report'].get_action(self, rep_name)
        rep_action['data'] = custom_data
        return rep_action


class StockProductionLotLabelWizardLine(models.TransientModel):
    _name = 'stock.production.lot.label.wizard.line'

    wiz_id = fields.Many2one(
        'stock.production.lot.label.wizard', 'Wizard')
    product_id = fields.Many2one(
        'product.product', 'Product')
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number')
    partner_id = fields.Many2one(
        'res.partner', 'Supplier')
    expected_use = fields.Selection([
        ('raw', 'Raw materials'),
        ('auxiliary', 'Auxiliary materials'),
        ('packaging', 'Packaging materials'),
        ('semifinished', 'Semi-finished goods'),
        ('finished', 'Finished goods')], string='Label type')
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.user.company_id)
    product_name = fields.Char('Code and description')
    lot_name = fields.Char('Lot/Serial Number')
    use_date = fields.Date('Use date')
    extended_shelf_life_date = fields.Date('Extended shelf life date')
    partner_name = fields.Char('Supplier name')
    origin = fields.Char('Origin')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            product_name = self.product_id.name
            if self.product_id.code:
                product_name = '[%s] %s' % (self.product_id.code, self.product_id.name)
            self.product_name = product_name
            if self.product_id != self.lot_id.product_id:
                self.lot_id = False
            self.expected_use = self.product_id.expected_use

    @api.onchange('lot_id')
    def onchange_lot_id(self):
        if self.lot_id:
            self.lot_name = self.lot_id.name
            self.use_date = self.lot_id.use_date
            self.extended_shelf_life_date = self.lot_id.extended_shelf_life_date
            if self.product_id != self.lot_id.product_id:
                self.product_id = self.lot_id.product_id

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.partner_name = self.partner_id.name

    @api.onchange('use_date')
    def onchange_use_date(self):
        if self.use_date and self.product_id and not self.lot_id:
            use_date = fields.Datetime.from_string(self.use_date)
            duration = self.product_id.extended_shelf_life_time or 0
            date = False
            if duration:
                date = use_date + timedelta(days=duration)
            self.extended_shelf_life_date = date


class StockProductionLotLabelWizardParser(models.AbstractModel):
    _name = 'report.stock_production_lot_label_wizard.stock_production_lot_label_report'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report_name = 'eln_reports.stock_production_lot_label_report'
        if not data:
            raise exceptions.Warning(_('Error'),
                _('You must print it from a wizard'))
        docs = self.env['stock.production.lot.label.wizard.line'].browse(data['line_ids'])
        docargs = {
            'doc_ids': [],
            'doc_model': 'stock.production.lot.label.wizard.line',
            'docs': docs,
        }
        return report_obj.render(report_name, docargs)

