# -*- coding: utf-8 -*-
# Copyright 2017 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.osv import osv, fields
from datetime import datetime
from openerp.tools.translate import _


class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    def _get_indicators(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, {'lead_time': 0.0, 'overweight': 0.0, 'scrap_usage': 0.0})
        pc_obj = self.pool.get('performance.calculation')
        for production in self.browse(cr, uid, ids, context=context):
            if production.state != 'done':
                continue
            # lead time
            create_date = datetime.strptime(production.create_date, '%Y-%m-%d %H:%M:%S')
            wl_date_finished = production.workcenter_lines.mapped('date_finished')
            date_finished = wl_date_finished and all(wl_date_finished) and datetime.strptime(max(wl_date_finished), '%Y-%m-%d %H:%M:%S')
            lead_time = date_finished and (date_finished - create_date)
            lead_time = lead_time and round(lead_time.total_seconds() / 3600, 2)
            # overweight
            overweight = pc_obj._get_overweight(cr, uid, ids, production, context=context)['overweight']
            # scrap & usage
            result = pc_obj._get_scrap_and_usage(cr, uid, ids, production, context=context)
            res[production.id]['lead_time'] = lead_time
            res[production.id]['overweight'] = overweight
            res[production.id]['ind_scrap'] = result['scrap']
            res[production.id]['ind_usage'] = result['usage']
        return res

    _columns = {
        'lead_time': fields.function(_get_indicators, type="float", string="Lead time (h)", readonly=True, multi='indicators'),
        'overweight': fields.function(_get_indicators, type="float", string="Overweight (%)", readonly=True, multi='indicators'),
        'ind_scrap': fields.function(_get_indicators, type="float", string="Indicator Scrap", readonly=True, multi='indicators'),
        'ind_usage': fields.function(_get_indicators, type="float", string="Indicator Usage", readonly=True, multi='indicators'),
    }


class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'

    def _get_indicators(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, {'availability': 0.0, 'performance': 0.0, 'quality': 0.0, 'oee': 0.0})
        pc_obj = self.pool.get('performance.calculation')
        for wl in self.browse(cr, uid, ids, context=context):
            if wl.state != 'done':
                continue
            availability, performance, quality, oee = pc_obj._get_oee(cr, uid, ids, wl, context=context)
            res[wl.id]['availability'] = availability
            res[wl.id]['performance'] = performance
            res[wl.id]['quality'] = quality
            res[wl.id]['oee'] = oee
        return res

    _columns = {
        'availability': fields.function(_get_indicators, type="float", string="Availability", readonly=True, multi='indicators'),
        'performance': fields.function(_get_indicators, type="float", string="Performance", readonly=True, multi='indicators'),
        'quality': fields.function(_get_indicators, type="float", string="Quality", readonly=True, multi='indicators'),
        'oee': fields.function(_get_indicators, type="float", string="OEE", readonly=True, multi='indicators'),
    }
