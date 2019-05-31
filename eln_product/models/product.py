# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from datetime import datetime
import openerp.addons.decimal_precision as dp


class ProductOptionsProduct(models.Model):
    _name = 'product.options.product'

    name = fields.Char('Name', size=64, required=True,
        default=lambda self: self.env['ir.sequence'].get('product.options.product') or '/')
    product_id = fields.Many2one('product.product', 'Product', ondelete='cascade')
    option_id = fields.Many2one('product.options', 'Option')


class ProductVerificationsProduct(models.Model):
    _name = 'product.verifications.product'

    name = fields.Char('Name', size=64, required=True,
        default=lambda self: self.env['ir.sequence'].get('product.verifications.product') or '/')
    product_id = fields.Many2one('product.product', 'Product', ondelete='cascade')
    verification_id = fields.Many2one('product.verifications', 'Verification')



class ProductRevisions(models.Model):
    _name = 'product.revision'

    name = fields.Char('Name', size=64, required=True,
        default=lambda self: self.env['ir.sequence'].get('product.revision') or '/')
    product_id = fields.Many2one('product.product', 'Product', ondelete='cascade')
    user_id = fields.Many2one('res.users', 'User',
        default=lambda self: self.env.user)
    date = fields.Date('Date', default=lambda s: fields.Date.context_today(s))
    description = fields.Text('Description')


class ProductSheetShipments(models.Model):
    _name = 'product.sheet.shipments'

    name = fields.Char('Name', size=64, required=True,
        default=lambda self: self.env['ir.sequence'].get('product.sheet.shipments') or '/')
    product_id = fields.Many2one('product.product', 'Product', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', 'Partner')
    date = fields.Date('Date', required=True)
    revision = fields.Char('Rev.', size=255, readonly=True)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_ingredient_ids = fields.One2many('product.ingredient', 'product_parent_id', string="Ingredients")
    protective_atmosphere = fields.Boolean('Protective atmosphere')
    perforated_bag = fields.Boolean('Perforated bag')
    energy = fields.Float('Energy', digits=dp.get_precision('Product Unit of Measure'))
    carbohydrates = fields.Float('Carbohydrates', digits=dp.get_precision('Product Unit of Measure'))
    carbo_sugar = fields.Float('of which sugars', digits=dp.get_precision('Product Unit of Measure'))
    fats = fields.Float('Fats', digits=dp.get_precision('Product Unit of Measure'))
    fat_saturates = fields.Float('of which saturates', digits=dp.get_precision('Product Unit of Measure'))
    proteins = fields.Float('Proteins', digits=dp.get_precision('Product Unit of Measure'))
    salt = fields.Float('Salt', digits=dp.get_precision('Product Unit of Measure'))
    storage_conditions = fields.Text('Storage conditions', translate=True)
    expected_use = fields.Text('Expected use', translate=True)
    allergen = fields.Text('Allergen', translate=True)
    ogms = fields.Text('OGMs', translate=True)
    comments_product_sheet = fields.Char('Comments (product sheet)', size=255, translate=True)
    comments_sheet = fields.Char('Comments (sheet)', size=255, translate=True)
    comments_product_logistics_sheet = fields.Char('Comments (product logistics sheet)', size=255, translate=True)
    palletizing = fields.Binary('Palletizing')
    provision_boxes_base = fields.Binary('Provision of boxes base')
    format = fields.Char('Format', size=64, translate=True)
    comercial_format = fields.Char('Comercial format', size=255, translate=True)
    bag_length = fields.Char('Bag length', size=64)
    box = fields.Many2one('product.product', string='Box', company_dependent=True)
    bobbin = fields.Many2one('product.product', string='Bobbin', company_dependent=True)
    bag = fields.Many2one('product.product', string='Bag', company_dependent=True)
    others = fields.Many2one('product.product', string='Others', company_dependent=True)
    seal = fields.Many2one('product.product', string='Seal', company_dependent=True)
    allergen_labeling = fields.Boolean('Allergen labeling')
    gluten_free_labeling = fields.Boolean('Gluten free labeling')
    parameter_ids = fields.One2many('product.parameter.product', 'product_id', string='Parameters')
    option_ids = fields.One2many('product.options.product', 'product_id', string='Options')
    verification_ids = fields.One2many('product.verifications.product', 'product_id', string='Verifications')
    revision_ids = fields.One2many('product.revision', 'product_id', string='Revisions')
    shipments_ids = fields.One2many('product.sheet.shipments', 'product_id', string='Shipments')
    partner_product_code = fields.Char('Partner code', size=64)
    dun14 = fields.Char('DUN14', size=64)
    last_revision = fields.Char(string='Last revision', compute='_get_last_revision', size=255, readonly=True)
    last_revision_ldm = fields.Char(string='Last revision LdM', compute='_get_last_revision_ldm', size=255, readonly=True)
    development_code = fields.Char('Development code', size=64)
    written_by = fields.Many2one('hr.employee', string='Written by')
    written_signature = fields.Binary(compute='_get_signature', readonly=True)
    written_job = fields.Many2one('hr.job', string='Job')
    reviewed_by = fields.Many2one('hr.employee',  string='Reviewed by')
    reviewed_signature = fields.Binary(compute='_get_signature', readonly=True)
    reviewed_job = fields.Many2one('hr.job', string='Job')
    approved_by = fields.Many2one('hr.employee', string='Approved by')
    approved_signature = fields.Binary(compute='_get_signature', readonly=True)
    approved_job = fields.Many2one('hr.job', string='Job')
    recommended_ration = fields.Integer('Recommended ration (g)')
    qty_dispo = fields.Float(
        string='Stock available',
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_product_dispo',
        help="Stock available for assignment. It refers to the actual stock not reserved.")
    pallet_boxes_layer = fields.Integer('Boxes per layer')
    pallet_layers = fields.Integer('Layers per pallet')
    pallet_boxes_pallet = fields.Integer('Boxes per pallet')
    pallet_gross_weight = fields.Float('Gross weight (kg)', digits=(16,3))
    pallet_net_weight = fields.Float('Net weight (kg)', digits=(16,3))
    pallet_total_height = fields.Float('Total height (mm)', digits=(16,0))
    pallet_total_width = fields.Float('Total width (mm)', digits=(16,0))
    pallet_total_length = fields.Float('Total length (mm)', digits=(16,0))
    pallet_ul = fields.Many2one('product.ul', string='Pallet type')
    box_units = fields.Integer('Units per box')
    box_gross_weight = fields.Float('Gross weight (kg)', digits=(16,3))
    box_net_weight = fields.Float('Net weight (kg)', digits=(16,3))
    box_total_height = fields.Float('Total height (mm)', digits=(16,0))
    box_total_width = fields.Float('Total width (mm)', digits=(16,0))
    box_total_length = fields.Float('Total length (mm)', digits=(16,0))
    box_ul = fields.Many2one('product.ul', string='Box type')
    unit_gross_weight = fields.Float('Gross weight (g)', digits=(16,3))
    unit_net_weight = fields.Float('Net weight (g)', digits=(16,3))
    unit_net_weight_drained = fields.Float('Net drained weight (g)', digits=(16,3),
        help='The drained net weight in g. Leave zero if not applicable.')
    unit_total_height = fields.Float('Total height (mm)', digits=(16,0))
    unit_total_width = fields.Float('Total width (mm)', digits=(16,0))
    unit_total_length = fields.Float('Total length (mm)', digits=(16,0))
    ramp_up_date = fields.Date('Ramp Up Date', copy=False,
        default=lambda s: fields.Date.context_today(s))

    @api.multi
    def _get_last_revision(self):
        for product in self:
            last_revision = ''
            revision = self.env['product.revision'].search([('product_id', '=', product.id)], order='date desc', limit=1)
            if revision.date:
                revision_date = datetime.strptime(revision.date, '%Y-%m-%d')
                last_revision = revision.name + ' (' + revision_date.strftime('%d/%m/%Y') + ')'
            product.last_revision = last_revision

    @api.multi
    def _get_last_revision_ldm(self):
        for product in self:
            last_revision = ''
            revision = self.env['mrp.bom'].search([('product_id', '=',  product.id)], order='date_start desc', limit=1)
            if revision.date_start:
                revision_date = datetime.strptime(revision.date_start, '%Y-%m-%d')
                last_revision = revision.name + ' (' + revision_date.strftime('%d/%m/%Y') + ')'
            product.last_revision_ldm = last_revision

    @api.multi
    def _get_signature(self):
        for product in self:
            product.written_signature = product.written_by.user_id.signature_image
            product.reviewed_signature = product.reviewed_by.user_id.signature_image
            product.approved_signature = product.approved_by.user_id.signature_image

    @api.multi
    def _product_dispo(self):
        for product in self:
            qty_dispo = product.qty_available - product.outgoing_qty
            product.qty_dispo = qty_dispo if qty_dispo > 0.0 else 0.0

    @api.onchange('ean13')
    def onchange_ean13(self):
        """
            Comprueba que no esté en uso ya el código ean introducido. Si lo está muestra un aviso
        """
        if self.ean13:
            product_ids = self.search([('ean13', '=', self.ean13), ('id', '!=', self._origin.id), ('active', '=', True)], limit=100)
            if product_ids:
                cadena = '| '
                for product_id in product_ids:
                    cadena += product_id.default_code + ' | '
                warning = {
                    'title': _('Warning!'),
                    'message' : _('The EAN-13 code you entered is already in use.\nThe references of related products are: %s') % (cadena)
                }
                return {'warning': warning}

    @api.onchange('dun14')
    def onchange_dun14(self):
        """
            Comprueba que no esté en uso ya el código dun introducido. Si lo está muestra un aviso
        """
        if self.dun14:
            product_ids = self.search([('dun14', '=', self.dun14), ('id', '!=', self._origin.id), ('active', '=', True)], limit=100)
            if product_ids:
                cadena = '| '
                for product_id in product_ids:
                    cadena += product_id.default_code + ' | '
                warning = {
                    'title': _('Warning!'),
                    'message' : _('The DUN-14 code you entered is already in use.\nThe references of related products are: %s') % (cadena)
                }
                return {'warning': warning}

    @api.onchange('written_by')
    def onchange_written_by(self):
        self.written_job = self.written_by.job_id

    @api.onchange('reviewed_by')
    def onchange_reviewed_by(self):
        self.reviewed_job = self.reviewed_by.job_id

    @api.onchange('approved_by')
    def onchange_approved_by(self):
        self.approved_job = self.approved_by.job_id

    @api.onchange('state')
    def onchange_state(self):
        if self.state == 'draft':
            self.ramp_up_date = False
        elif self.state == 'sellable' and self.ramp_up_date == False:
            self.ramp_up_date = fields.Date.context_today(self)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    uos_coeff = fields.Float(digits=(16,10))

