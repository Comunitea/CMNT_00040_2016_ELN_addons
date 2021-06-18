# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from datetime import datetime
import openerp.addons.decimal_precision as dp


class ProductTechnicalSheet(models.Model):
    _name = 'product.technical.sheet'
    _order = 'product_id, sequence'

    name = fields.Char('Name', size=255, required=True)
    product_id = fields.Many2one('product.product', 'Product')
    sequence = fields.Integer('Sequence', default=1)
    product_ingredient_ids = fields.One2many(
        'product.ingredient', 'product_technical_sheet_id', 'Ingredients',
        copy=True)
    protective_atmosphere = fields.Boolean('Protective atmosphere')
    perforated_bag = fields.Boolean('Perforated bag')
    energy_kcal = fields.Float('Energy (kcal)', digits=(16,3))
    energy_kj = fields.Float('Energy (kJ)', digits=(16,3))
    carbohydrates = fields.Float('Carbohydrates', digits=(16,3))
    carbo_sugar = fields.Float('of which sugars', digits=(16,3))
    fats = fields.Float('Fats', digits=(16,3))
    fat_saturates = fields.Float('of which saturates', digits=(16,3))
    proteins = fields.Float('Proteins', digits=(16,3))
    salt = fields.Float('Salt', digits=(16,3))
    storage_conditions = fields.Text('Storage conditions', translate=True)
    expected_use = fields.Text('Expected use', translate=True)
    allergen = fields.Text('Allergen', translate=True)
    ogms = fields.Text('OGMs', translate=True)
    comments = fields.Char('Comments', size=255, translate=True)
    commercial_format = fields.Char('Commercial format', size=255, translate=True)
    allergen_labeling = fields.Boolean('Allergen labeling')
    gluten_free_labeling = fields.Boolean('Gluten free labeling')
    parameter_ids = fields.One2many(
        'product.parameter.product', 'product_technical_sheet_id', 'Parameters',
        copy=True)
    revision_ids = fields.One2many(
        'product.revision', 'product_technical_sheet_id', 'Revisions')
    last_revision = fields.Char(string='Last revision', compute='_get_last_revision', size=255, readonly=True)
    last_revision_ldm = fields.Char(string='Last revision LdM', compute='_get_last_revision_ldm', size=255, readonly=True)
    written_by = fields.Many2one('hr.employee', string='Written by', copy=False)
    written_signature = fields.Binary(compute='_get_signature', readonly=True)
    written_job = fields.Many2one('hr.job', string='Job', copy=False)
    reviewed_by = fields.Many2one('hr.employee',  string='Reviewed by', copy=False)
    reviewed_signature = fields.Binary(compute='_get_signature', readonly=True)
    reviewed_job = fields.Many2one('hr.job', string='Job', copy=False)
    approved_by = fields.Many2one('hr.employee', string='Approved by', copy=False)
    approved_signature = fields.Binary(compute='_get_signature', readonly=True)
    approved_job = fields.Many2one('hr.job', string='Job', copy=False)
    recommended_ration = fields.Integer('Recommended ration (g)')
    net_weight = fields.Float('Net weight (g)', digits=(16,3))
    net_weight_drained = fields.Float('Net drained weight (g)', digits=(16,3),
        help='The drained net weight in g. Leave zero if not applicable.')
    nutriscore = fields.Selection([
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D'),
        ('e', 'E'),
        ], string='Nutri-Score')
    company_id = fields.Many2one(
        'res.company', 'Company',
        related='product_id.company_id',
        readonly=True, store=True)

    @api.multi
    def _get_last_revision(self):
        for sheet in self:
            last_revision = ''
            domain = [('product_technical_sheet_id', '=', sheet.id)]
            revision = self.env['product.revision'].search(domain, order='date desc', limit=1)
            if revision.date:
                revision_date = datetime.strptime(revision.date, '%Y-%m-%d')
                last_revision = revision.name + ' (' + revision_date.strftime('%d/%m/%Y') + ')'
            sheet.last_revision = last_revision

    @api.multi
    def _get_last_revision_ldm(self):
        for sheet in self:
            last_revision = ''
            domain = [('product_id', '=',  sheet.product_id.id)]
            revision = self.env['mrp.bom'].search(domain, order='date_start desc', limit=1)
            if revision.date_start:
                revision_date = datetime.strptime(revision.date_start, '%Y-%m-%d')
                last_revision = revision.name + ' (' + revision_date.strftime('%d/%m/%Y') + ')'
            sheet.last_revision_ldm = last_revision

    @api.multi
    def _get_signature(self):
        for sheet in self:
            sheet.written_signature = sheet.written_by.user_id.signature_image
            sheet.reviewed_signature = sheet.reviewed_by.user_id.signature_image
            sheet.approved_signature = sheet.approved_by.user_id.signature_image

    @api.onchange('written_by')
    def onchange_written_by(self):
        self.written_job = self.written_by.job_id

    @api.onchange('reviewed_by')
    def onchange_reviewed_by(self):
        self.reviewed_job = self.reviewed_by.job_id

    @api.onchange('approved_by')
    def onchange_approved_by(self):
        self.approved_job = self.approved_by.job_id

    @api.onchange('energy_kj')
    def onchange_energy_kj(self):
        if self.energy_kj and not self.energy_kcal:
            self.energy_kcal = self.energy_kj / 4.187

    @api.onchange('energy_kcal')
    def onchange_energy_kcal(self):
        if self.energy_kcal and not self.energy_kj:
            self.energy_kj = self.energy_kcal * 4.187

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        if 'name' not in default:
            default['name'] = _("%s (copy)") % (self['name'])
        return super(ProductTechnicalSheet, self).copy(default=default)
