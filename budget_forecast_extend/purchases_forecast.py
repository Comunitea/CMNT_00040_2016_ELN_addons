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
from openerp.osv import orm
from openerp.tools.translate import _


class purchases_forecast(orm.Model):
    _inherit = 'purchases.forecast'

    def _prepare_budget_vals(self, cr, uid, cur, context=None):
        vals = super(purchases_forecast, self)._prepare_budget_vals(cr, uid, cur, context)
        for line in cur.purchases_forecast_lines:
            for month in ['jan_amount', 'feb_amount', 'mar_amount',
                          'apr_amount', 'may_amount', 'jun_amount',
                          'jul_amount', 'aug_amount', 'sep_amount',
                          'oct_amount', 'nov_amount', 'dec_amount']:
                if month not in vals.keys():
                    vals[month] = 0.0
                vals[month] += float(round(line[month + '_total'],2))
        return vals
