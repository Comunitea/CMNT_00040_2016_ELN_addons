# -*- coding: utf-8 -*-
# Copyright 2020 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from datetime import datetime


class QcInspection(models.Model):
    _inherit = 'qc.inspection'

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
            make_inspection = True if object_ref.picking_id.purchase_id else False
            if not make_inspection:
                return self.env['qc.inspection']
        return super(QcInspection, self)._make_inspection(object_ref, trigger_line)


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

