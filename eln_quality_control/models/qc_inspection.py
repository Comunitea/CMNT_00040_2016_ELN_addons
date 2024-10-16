# -*- coding: utf-8 -*-
# Copyright 2020 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from datetime import datetime


class QcInspection(models.Model):
    _inherit = 'qc.inspection'
    _order = 'name desc'

    auto_generated = fields.Boolean(
        states={'draft': [('readonly', False)]})
    user = fields.Many2one(
        track_visibility=False)
    approved_date = fields.Datetime(
        string='Approved date',
        readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'ready': [('readonly', False)]},
        select=True)
    approved_by = fields.Many2one(
        'res.users', 'Approved by',
        readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'ready': [('readonly', False)]})
    uom_id = fields.Many2one(
        comodel_name='product.uom', string='UoM')

    @api.multi
    def action_confirm(self):
        for inspection in self:
            if not inspection.approved_date:
                inspection.approved_date = datetime.today()
            if not inspection.approved_by:
                inspection.approved_by = self.env.user
        return super(QcInspection, self).action_confirm()

    @api.multi
    def action_approve(self):
        for inspection in self:
            if not inspection.approved_date:
                inspection.approved_date = datetime.today()
            if not inspection.approved_by:
                inspection.approved_by = self.env.user
        return super(QcInspection, self).action_approve()

    @api.multi
    def _make_inspection(self, object_ref, trigger_line):
        if (trigger_line.test.only_purchases and 
                trigger_line.trigger.picking_type.code == 'incoming' and
                object_ref and object_ref._name == 'stock.pack.operation'):
            purchase_line_ids = object_ref.picking_id.move_lines.mapped('purchase_line_id')
            make_inspection = True if purchase_line_ids else False
            #make_inspection = True if object_ref.picking_id.purchase_id else False
            if not make_inspection:
                return self.env['qc.inspection']
        if object_ref and object_ref._name == 'stock.move':
            make_inspection = (object_ref.location_dest_id.usage == 'internal')
            if not make_inspection:
                return self.env['qc.inspection']
        return super(QcInspection, self)._make_inspection(object_ref, trigger_line)

    @api.multi
    def _prepare_inspection_header(self, object_ref, trigger_line):
        res = super(QcInspection, self)._prepare_inspection_header(
            object_ref, trigger_line)
        # Fill UoM when coming from pack operations
        if object_ref and object_ref._name == 'stock.pack.operation':
            res['uom_id'] = object_ref.product_uom_id.id
        if object_ref and object_ref._name == 'stock.move':
            res['uom_id'] = object_ref.product_uom.id
        return res

    @api.onchange('object_id')
    def onchange_object_id(self):
        if self.object_id:
            if self.object_id._name == 'stock.move':
                self.uom_id = self.object_id.product_uom
            elif self.object_id._name == 'stock.pack.operation':
                self.uom_id = self.object_id.product_uom_id
        return super(QcInspection, self).onchange_object_id()


class QcInspectionLine(models.Model):
    _inherit = 'qc.inspection.line'

    company_id = fields.Many2one(
        'res.company', 'Company',
        related='inspection_id.company_id',
        readonly=True, store=True)

    @api.multi
    def unlink(self):
        res = super(QcInspectionLine, self).unlink()
        self.env['qc.test.question.value'].unlink_orphan_values()
        return res

