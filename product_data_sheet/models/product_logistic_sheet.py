# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _


class ProductLogisticSheet(models.Model):
    _name = 'product.logistic.sheet'
    _order = 'product_id, sequence'

    name = fields.Char('Name', size=255, required=True)
    product_id = fields.Many2one('product.product', 'Product')
    sequence = fields.Integer('Sequence', default=1)
    palletizing = fields.Binary('Palletizing')
    provision_boxes_base = fields.Binary('Provision of boxes base')
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
    comments = fields.Char('Comments', size=255, translate=True)
    company_id = fields.Many2one(
        'res.company', 'Company',
        related='product_id.company_id',
        readonly=True, store=True)

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        if 'name' not in default:
            default['name'] = _("%s (copy)") % (self['name'])
        return super(ProductLogisticSheet, self).copy(default=default)
