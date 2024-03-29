# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2016 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp import models, fields
from openerp import tools
import openerp.addons.decimal_precision as dp
from ..models.mrp import PRODUCTION_TYPES


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    product_weight = fields.Float('Product Weight',
        digits=dp.get_precision('Stock Weight'),
        readonly=True)
    planified_time = fields.Float('Planified time',
        readonly=True)
    production_lead_time = fields.Float('Production Lead time',
        group_operator='avg', readonly=True)
    production_type = fields.Selection(PRODUCTION_TYPES, 'Type of production',
        readonly=True)
    date_start = fields.Date('Start Date',
        readonly=True)
    company_id = fields.Many2one('res.company', 'Company',
        readonly=True)

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'mrp_workorder')
        cr.execute("""
            create or replace view mrp_workorder as (
                select
                    date(wl.date_planned) as date,
                    date(wl.date_start) as date_start,
                    min(wl.id) as id,
                    mp.product_id as product_id,
                    sum(wl.hour) as total_hours,
                    avg(wl.delay) as delay,
                    (w.costs_hour*sum(wl.hour)) as total_cost,
                    wl.production_id as production_id,
                    wl.workcenter_id as workcenter_id,
                    sum(wl.cycle) as total_cycles,
                    count(*) as nbr,
                    sum(mp.product_qty) as product_qty,
                    sum(mp.product_qty*pt.weight_net) as product_weight,
                    sum(extract(epoch from wl.date_finished - wl.date_start)/3600)::decimal(16,2) as planified_time,
                    sum(extract(epoch from wl.date_finished - mp.create_date)/3600)::decimal(16,2) as production_lead_time,
                    mp.production_type as production_type,
                    wl.state as state,
                    mp.company_id as company_id
                from mrp_production_workcenter_line wl
                    left join mrp_workcenter w on (w.id = wl.workcenter_id)
                    left join mrp_production mp on (mp.id = wl.production_id)
                    left join product_product pp on (pp.id = mp.product_id)
                    left join product_template pt on (pt.id = pp.product_tmpl_id)
                group by
                    w.costs_hour, mp.product_id, mp.name, wl.state, wl.date_planned, wl.date_start, wl.production_id, wl.workcenter_id, mp.production_type, mp.company_id
        )""")
