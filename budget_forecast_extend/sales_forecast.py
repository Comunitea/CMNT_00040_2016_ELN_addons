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
from odoo.osv import orm, fields
from odoo.tools.translate import _


class sales_forecast(orm.Model):
    _inherit = 'sales.forecast'

    def create_budget_lines2(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        budget_line = self.pool.get('budget.line')

        for cur in self.browse(cr, uid, ids):
            if cur.sales_forecast_lines and not cur.is_merged:
                if not cur.budget_version_id or not cur.budget_item_id:
                    raise orm.except_orm(_('Error !'), _('For create a budget line is neccessary to have a budget version and budget item at sales forecast.'))
                vals = {
                        'budget_version_id': cur.budget_version_id.id,
                        'budget_item_id': cur.budget_item_id.id,
                        'name': _('Sales forecast line of ') + cur.name,
                        'amount': 0.0,
                        'currency_id': cur.budget_version_id.currency_id.id,
                        'jan_amount': 0.0,
                        'feb_amount': 0.0,
                        'mar_amount': 0.0,
                        'apr_amount': 0.0,
                        'may_amount': 0.0,
                        'jun_amount': 0.0,
                        'jul_amount': 0.0,
                        'aug_amount': 0.0,
                        'sep_amount': 0.0,
                        'oct_amount': 0.0,
                        'nov_amount': 0.0,
                        'dec_amount': 0.0,
                        'analytic_account_id': cur.analytic_id and cur.analytic_id.id or False,
                }
                for line in cur.sales_forecast_lines:
                    vals['amount'] += line.total_amount
                    for month in ['jan_amount', 'feb_amount', 'mar_amount',
                                  'apr_amount', 'may_amount', 'jun_amount',
                                  'jul_amount', 'aug_amount', 'sep_amount',
                                  'oct_amount', 'nov_amount', 'dec_amount']:
                        vals[month] += float(round(line[month], 2))
                budget_line.create(cr, uid, vals)

        return True

    def action_validate(self, cr, uid, ids, context=None):

        self.create_budget_lines2(cr, uid, ids, context)

        return super(sales_forecast, self).action_validate(cr, uid, ids, context=context)

    '''def action_done(self, cr, uid, ids, context=None):
        res = super(sales_forecast, self).action_done(cr, uid, ids, context)
        cost_line = self.pool.get('product.costs.line')
        forecast_line = self.pool.get('sales.forecast.line')
        for cur in self.browse(cr, uid, ids):
            if cur.sales_forecast_lines:
                for line in cur.sales_forecast_lines:
                    cost_warehouse = 0.0
                    cost_warehouse += cost_line._get_cost_raw_material(cr, uid, ids, line.product_id, context)
                    cost_warehouse += line.product_id.weight_net
                    cost_warehouse += cost_line._get_cost_productino_min(cr, uid, ids, line.product_id, context)
                    cost_structure = 0.0
                    cost_structure = cost_warehouse + line.product_id.weight_net
                    forecast_line.write(cr, uid, line.id, {'cost_warehouse': cost_warehouse, 'cost_structure': cost_structure})

        return res'''


class sales_forecast_line(orm.Model):
    _inherit = 'sales.forecast.line'
    _columns = {
        'cost_warehouse': fields.float('Cost Warehouse', digits=(16,2)),
        'cost_structure': fields.float('Cost Warehouse', digits=(16,2))
    }
