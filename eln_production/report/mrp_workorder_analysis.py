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
from openerp.osv import fields,osv
from openerp import tools
import openerp.addons.decimal_precision as dp


class mrp_workorder(osv.osv):
    _inherit = 'mrp.workorder'

    _columns = {
        'product_weight': fields.float('Product Weight', digits_compute=dp.get_precision('Stock Weight'), readonly=True),
        'planified_time': fields.float('Planified time', readonly=True),
        'production_lead_time': fields.float('Production Lead time', readonly=True, group_operator='avg'),
        'production_type': fields.selection([('normal','Normal'), ('rework','Rework'), ('sample','Sample'), ('special','Special')], 'Type of production', readonly=True),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'mrp_workorder')
        cr.execute("""
            create or replace view mrp_workorder as (
                select
                    date(wl.date_planned) as date,
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
                    wl.state as state
                from mrp_production_workcenter_line wl
                    left join mrp_workcenter w on (w.id = wl.workcenter_id)
                    left join mrp_production mp on (mp.id = wl.production_id)
                    left join product_product pp on (pp.id = mp.product_id)
                    left join product_template pt on (pt.id = pp.product_tmpl_id)
                group by
                    w.costs_hour, mp.product_id, mp.name, wl.state, wl.date_planned, wl.production_id, wl.workcenter_id, mp.production_type
        )""")
