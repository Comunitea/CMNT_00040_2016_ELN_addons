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
import openerp.addons.decimal_precision as dp


def rounding(f, r):
    if not r:
        return f
    return round(f / r) * r


class ProductProduct(models.Model):
    _inherit = 'product.product'

    cost_structure_id = fields.Many2one('cost.structure', string='Cost Structure', company_dependent=True)
    forecasted_price = fields.Float(string='Forecasted Cost Price',
        groups='base.group_user', digits=dp.get_precision('Product Price'),
        company_dependent=True,
        help="Forecasted cost price used to calculate an alternative BoM cost based on this value. If set to 0, the standard price is used instead.")
    cost_price_for_pricelist = fields.Float(string='Cost price for price list',
        groups='base.group_user', digits=dp.get_precision('Product Price'),
        company_dependent=True,
        help="Cost price for price list. Used, for example, to calculate product price list based on.")

    @api.multi
    def action_show_product_costs(self):
        self.ensure_one()
        pcl_obj = self.env['product.costs.line']
        value = pcl_obj.show_product_costs()
        return value

    @api.multi
    def action_get_product_costs(self):
        self.ensure_one()
        pcl_obj = self.env['product.costs.line']
        pcl_obj.get_product_costs()
        value = pcl_obj.show_product_costs()
        return value

    @api.multi
    def action_update_product_costs(self):
        self.ensure_one()
        pcl_obj = self.env['product.costs.line']
        ctx = self._context.copy()
        ctx.update(
            update_costs=True,
            register_costs=False,
        )
        value = pcl_obj.with_context(ctx).get_product_costs()
        return value

    @api.multi
    def reset_forecasted_price(self):
        self.ensure_one()
        product_ids = self.search([('forecasted_price', '!=', 0.0)])
        product_ids.write({'forecasted_price': 0.0})
        return True


class ProductCost(models.Model):
    _name = 'product.cost'
    _rec_name = "product_id"
    _order = 'date desc, id desc'

    product_id = fields.Many2one('product.product', string='Product Cost', required=True)
    product_cost_lines = fields.One2many('product.cost.lines', 'product_cost_id',
        string='Costs')
    date = fields.Datetime('Date', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id)


class ProductCostLines(models.Model):
    _name = 'product.cost.lines'
    _order = 'sequence, id'

    product_cost_id = fields.Many2one('product.cost', string='Cost', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', required=True)
    name = fields.Char('Name', size=255, required=True)
    theoric_cost = fields.Float('Theoric Cost',
        required=True, digits=dp.get_precision('Product Price'),
        default=0.0)
    forecasted_cost = fields.Float('Forecasted Cost',
        required=True, digits=dp.get_precision('Product Price'),
        default=0.0)
    tc_fc_percent = fields.Float(
        string=_('TC vs FC (%)'),
        digits=(4,2),
        compute='_cost_percent', default=0.0)
    inventory = fields.Boolean('Inventory', default=False)
    total = fields.Boolean('Total', default=False)
    company_id = fields.Many2one('res.company', string='Company',
        related='product_cost_id.company_id', store=True,
        readonly=True)

    @api.multi
    def _cost_percent(self):
        for prod_cost_line in self:
            tc_fc_percent = 100
            if prod_cost_line.forecasted_cost:
                tc_fc_percent = 100 * ((prod_cost_line.theoric_cost / prod_cost_line.forecasted_cost) - 1)
            prod_cost_line.tc_fc_percent = tc_fc_percent
