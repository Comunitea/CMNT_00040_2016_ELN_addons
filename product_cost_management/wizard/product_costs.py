# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 Pexego Sistemas Informáticos All Rights Reserved
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
from openerp import models, fields, api, exceptions, _
import time
from openerp.addons.decimal_precision import decimal_precision as dp


def rounding(f, r):
    if not r:
        return f
    return round(f / r) * r


class ProductCostsLine(models.TransientModel):
    _name = 'product.costs.line'

    name = fields.Char('Name', size=255, required=True)
    sequence = fields.Integer('Sequence', required=True)
    theoric_cost = fields.Float('Theoric Cost',
        required=True, digits=dp.get_precision('Product Price'),
        default=0.0)
    forecasted_cost = fields.Float('Forecasted Cost',
        required=True, digits=dp.get_precision('Product Price'),
        default=0.0)
    tc_fc_percent = fields.Float('TC vs FC (%)',
        readonly=True, digits=(4,2))
    inventory = fields.Boolean('Inventory')
    total = fields.Boolean('Total')

    @api.model
    def _get_costs(self, element_id=False, product_id=False, bom_id=False):
        theoric = 0.0
        forecasted = 0.0
        product_obj = self.env['product.product']
        uom_obj = self.env['product.uom']
        bom_obj = self.env['mrp.bom']
        if element_id and product_id:
            # THEORIC COST
            if element_id.cost_type == 'bom':
                if bom_id or product_id.bom_ids:
                    bom = bom_id or product_id.bom_ids[0]
                    factor = uom_obj._compute_qty(
                        bom.product_uom.id, bom.product_qty, product_id.uom_id.id)
                    res1, res2 = bom_obj._bom_explode(bom, product_id.id, factor / bom.product_qty, properties=[])
                    if res1:
                        for r in res1:
                            if r['product_id']:
                                productb = product_obj.browse(r['product_id'])
                                theoric += productb.standard_price * r['product_qty']
                                # Si el producto tiene lista de materiales y se usa en la estructura de costes
                                # calculamos de forma recursiva el valor forecasted_price
                                if 'bom' in productb.cost_structure_id.elements.mapped('cost_type'):
                                    ctx = self._context.copy()
                                    ctx.update(
                                        update_costs=False,
                                        register_costs=False,
                                        product_id=productb.id,
                                    )
                                    cost = self.with_context(ctx).get_product_costs()
                                    forecasted_price = cost.get('forecasted_price', False) or productb.forecasted_price or productb.standard_price or 0.0
                                else:
                                    forecasted_price = productb.forecasted_price or productb.standard_price or 0.0
                                forecasted += forecasted_price * r['product_qty']
                        theoric = theoric / (factor or 1.0)
                        forecasted = forecasted / (factor or 1.0)
            elif element_id.cost_type == 'standard_price':
                    theoric = product_id.standard_price or 0.0
                    forecasted = product_id.forecasted_price or product_id.standard_price or 0.0
            elif element_id.cost_type == 'ratio':
                if element_id.distribution_mode == 'eur':
                    theoric = element_id.cost_ratio * product_id.standard_price
                    forecasted = element_id.cost_ratio * (product_id.forecasted_price or product_id.standard_price or 0.0)
                elif element_id.distribution_mode == 'units':
                    theoric = element_id.cost_ratio
                    forecasted = theoric
                elif element_id.distribution_mode == 'kg':
                    theoric = element_id.cost_ratio * product_id.weight_net
                    forecasted = theoric
                elif element_id.distribution_mode == 'min':
                    if product_id.bom_ids:
                        bom = product_id.bom_ids[0]
                        if bom.routing_id:
                            hours = 0.0
                            for wc_use in bom.routing_id.workcenter_lines:
                                wc = wc_use.workcenter_id
                                qty_per_cycle = uom_obj._compute_qty(
                                    wc_use.uom_id.id, wc_use.qty_per_cycle, product_id.uom_id.id)
                                hour = (wc_use.hour_nbr / qty_per_cycle) * (wc_use.operators_number or 1.0)
                                hour = hour * (wc.time_efficiency or 1.0)
                                hour = hour / (wc.performance_factor or 1.0)
                                hour = hour / (bom.routing_id.availability_ratio or 1.0)
                                hour = float(hour)
                                hours += hour
                            theoric = element_id.cost_ratio * hours * 60
                            forecasted = theoric
            elif element_id.cost_type == 'total':
                theoric = 0.0
                forecasted = theoric
            elif element_id.cost_type == 'inventory':
                theoric = 0.0
                forecasted = theoric
        return theoric, forecasted

    @api.model
    def get_product_costs(self, bom_id=False):
        prod_obj = self.env['product.product']
        prod_cost_obj = self.env['product.cost']
        prod_cost_lines_obj = self.env['product.cost.lines']
        value = {}
        to_update_costs = []
        if self._context.get('product_id', False):
            product_ids = prod_obj.browse(self._context.get('product_id'))
        else:
            product_ids = prod_obj.search([('cost_structure_id', '!=', False)])
        for product in product_ids:
            if product.cost_structure_id and product.cost_structure_id.elements:
                if self._context.get('register_costs', True):
                    new_prod_cost_id = prod_cost_obj.create({
                        'product_id': product.id,
                        'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'company_id': product.cost_structure_id.company_id.id
                    })
                elements = product.cost_structure_id.elements
                sumtheo = 0.0
                sumforecasted = 0.0
                theoric = 0.0
                forecasted = 0.0
                for element in elements:
                    if element.cost_type not in ('total', 'inventory'):
                        theoric, forecasted = self._get_costs(element, product, bom_id)
                        sumtheo += theoric
                        sumforecasted += forecasted
                    else:
                        theoric = sumtheo
                        forecasted= sumforecasted
                    if self._context.get('register_costs', True):
                        vals = {
                            'product_cost_id': new_prod_cost_id.id,
                            'sequence': element.sequence,
                            'name': element.cost_type_id.name,
                            'theoric_cost': theoric,
                            'forecasted_cost': forecasted,
                            'inventory': (element.cost_type == 'inventory'),
                            'total': (element.cost_type in ('total', 'inventory'))
                        }
                        prod_cost_lines_obj.create(vals)
                    if element.cost_type == 'inventory': # Es el valor a usar para actualizar los costes en la producción
                        value = {
                            'inventory_cost': theoric,
                            'forecasted_price': forecasted
                        }
                    if self._context.get('update_costs', False) and element.cost_type == 'total':
                        to_update_costs.append((product, forecasted))
        if to_update_costs:
            for (product, forecasted) in to_update_costs:
                product.write({'cost_price_for_pricelist': forecasted})
        return value

    @api.model
    def show_product_costs(self):
        prod_cost_obj = self.env['product.cost']
        prod_cost_lines_obj = self.env['product.cost.lines']
        lines = []
        if self._context.get('product_id', False):
            domain = [('product_id', '=', self._context['product_id'])]
            cost_id = prod_cost_obj.search(domain, order='date desc', limit=1)
            if not cost_id:
                raise exceptions.Warning(_('Warning !'), _('Could not show costs. There are no costs associated with this product!'))
            domain = [('product_cost_id', '=', cost_id.id)]
            cost_lines = prod_cost_lines_obj.search(domain, order='sequence asc')
            if not cost_lines:
                raise exceptions.Warning(_('Warning !'), _('Could not show costs. No cost lines were found for this product!'))
            for l in cost_lines:
                vals = {
                    'sequence': l.sequence,
                    'name': l.name,
                    'theoric_cost': l.theoric_cost,
                    'forecasted_cost': l.forecasted_cost,
                    'tc_fc_percent': l.tc_fc_percent,
                    'inventory': l.inventory,
                    'total': l.total
                }
                new_id = self.create(vals)
                lines.append(new_id.id)
        value = {
            'domain': str([('id', 'in', lines)]),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'product.costs.line',
            'type': 'ir.actions.act_window',
            'nodestroy': True
        }
        return value


class UpdateProductCosts(models.TransientModel):
    _name = 'update.product.costs'

    @api.multi
    def action_update_product_costs_wzd(self):
        pcl_obj = self.env['product.costs.line']
        ctx = self._context.copy()
        ctx.update(
            update_costs=True,
            register_costs=False,
        )
        pcl_obj.with_context(ctx).get_product_costs()
        return True

    @api.multi
    def action_update_product_costs_cron(self):
        pcl_obj = self.env['product.costs.line']
        for company_id in self.env['res.company'].search([]):
            ctx = self._context.copy()
            ctx.update(
                update_costs=True,
                register_costs=False,
                force_company=company_id.id,
            )
            pcl_obj.with_context(ctx).get_product_costs()
        return True
