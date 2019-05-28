# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved.
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    remaining_samples = fields.Float(
         string='Samples',
         digits=dp.get_precision('Product Unit of Measure'),
         compute='_get_product_samples', readonly=True,
         help="Given Samples (in UoM)")

    @api.multi
    def _get_product_samples(self):
        """
            Gets remaining samples checking sale order lines with its product and checkbox 'Sample?' check
        """
        wh_ids = self.env['stock.warehouse'].search([('samples_loc_id', '!=', False)])
        samp_ids = wh_ids.mapped('samples_loc_id.id')
        for product in self:
            qty = round(product.with_context(location=samp_ids, warehouse=False).qty_available, 2)
            product.remaining_samples = qty

