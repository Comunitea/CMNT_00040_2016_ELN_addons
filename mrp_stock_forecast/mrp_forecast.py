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
############################################################################
from openerp.osv import osv, fields
import time
from openerp import netsvc
from openerp.tools.translate import _

class mrp_forecast(osv.osv):
    _name = 'mrp.forecast'
    _description = 'Forecast of producion hours'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'date': fields.date('Date'),
        'mrp_forecast_lines': fields.one2many('mrp.forecast.line',
                                                'mrp_forecast_id', 'Lines'),
        'company_id': fields.many2one('res.company', 'Company'),
        'state': fields.selection([
                                ('draft','Draft'),
                                ('approve', 'Approved'),
                                ('cancel', 'Cancel')], string="State",
                                required=True, readonly=True),
        'year': fields.integer('Year', size=4),
        'merged_into_id': fields.many2one('mrp.forecast', 'Merged into', required=False, readonly=True),
        'merged_from_ids': fields.one2many('mrp.forecast', 'merged_into_id', 'Merged from', readonly=True),
    }
    _defaults = {
        'state': 'draft',
    }

    def action_validate(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approve'})
        return True

    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

    def do_merge(self, cr, uid, ids, context=None):


        wf_service = netsvc.LocalService("workflow")
        forecast_obj = self.pool.get('mrp.forecast')
        forecast_line_obj = self.pool.get('mrp.forecast.line')

        old_ids = []
        res = {}
        lines = []
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id and self.pool.get('res.users').browse(cr, uid, uid).company_id.id or False
        new_id = forecast_obj.create(cr, uid, {'name': _('MRP forecast MERGED. '),
                                                   #'analytic_id': cur.analytic_id.id,
                                                   'date': time.strftime('%d-%m-%Y'),
                                                   'company_id': company,
                                                   'state': 'draft'
                                                    })

        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        for porder in self.browse(cr, uid, ids, context=context):
            forecast_obj.write(cr, uid, porder.id,{'merged_into_id': new_id})
            old_ids.append(porder.id)
            for l in porder.mrp_forecast_lines:
                lines.append(l.id)
        if lines:
            for line in forecast_line_obj.browse(cr, uid, lines):
                if not res.get(line.workcenter_id.id):
                    res[line.workcenter_id.id] = {}
                for month in range(0,12):
                    if not res[line.workcenter_id.id].get(months[month] + '_real_time'):
                        res[line.workcenter_id.id][months[month] + '_real_time'] = 0.0
                    if not res[line.workcenter_id.id].get(months[month] + '_hours'):
                        res[line.workcenter_id.id][months[month] + '_hours'] = 0.0
                    res[line.workcenter_id.id][months[month] + '_real_time'] = res[line.workcenter_id.id][months[month] + '_real_time'] + (eval('o.' + (months[month] + '_real_time'),{'o': line}))
                    res[line.workcenter_id.id][months[month] + '_hours'] = res[line.workcenter_id.id][months[month] + '_hours'] + (eval('o.' + (months[month] + '_hours'),{'o': line}))


        #res = {product_id:{'ene_qty': 100.00, 'feb_qty':2500.00}}
        if res:
            for workcenter in res:
                nwline = forecast_line_obj.create(cr, uid, {
                                'mrp_forecast_id': new_id,

                                'workcenter_id': workcenter})
                for month in range(0,12):
                    forecast_line_obj.write(cr, uid, nwline, {
                               months[month] + '_hours': res[workcenter][months[month] + '_hours'],
                               months[month] + '_real_time': res[workcenter][months[month] + '_real_time']})

            # make triggers pointing to the old purchases forecast to the new forecast
        if old_ids:
            for old_id in old_ids:
                wf_service.trg_validate(uid, 'mrp.forecast', old_id, 'action_cancel', cr)
        return new_id

mrp_forecast()

class mrp_forecast_line(osv.osv):
    _name = 'mrp.forecast.line'
    
    def _get_total_hours(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.jan_hours + line.feb_hours + line.mar_hours + \
                           line.apr_hours + line.may_hours + line.jun_hours + \
                           line.jul_hours + line.aug_hours + line.sep_hours + \
                           line.oct_hours + line.nov_hours + line.dec_hours
        return res

    def _get_total_real_time(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.jan_real_time + line.feb_real_time + line.mar_real_time + \
                           line.apr_real_time + line.may_real_time + line.jun_real_time + \
                           line.jul_real_time + line.aug_real_time + line.sep_real_time + \
                           line.oct_real_time + line.nov_real_time + line.dec_real_time
        return res

    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'mrp_forecast_id': fields.many2one('mrp.forecast', 'MRP Forecast', required=True, ondelete='cascade'),
        'workcenter_id': fields.many2one('mrp.workcenter', 'Workcenter', required=True),
        'jan_hours': fields.float('Jan Hrs'),
        'feb_hours': fields.float('Feb Hrs'),
        'mar_hours': fields.float('Mar Hrs'),
        'apr_hours': fields.float('Apr Hrs'),
        'may_hours': fields.float('May Hrs'),
        'jun_hours': fields.float('Jun Hrs'),
        'jul_hours': fields.float('Jul Hrs'),
        'aug_hours': fields.float('Aug Hrs'),
        'sep_hours': fields.float('Sep Hrs'),
        'oct_hours': fields.float('Oct Hrs'),
        'nov_hours': fields.float('Nov Hrs'),
        'dec_hours': fields.float('Dec Hrs'),
        'total_hours': fields.function(_get_total_hours, type="float", digits=(16,2), string="Total Hrs", readonly=True, store=True),

        'jan_real_time': fields.float('Jan Real Time'),
        'feb_real_time': fields.float('Feb Real Time'),
        'mar_real_time': fields.float('Mar Real Time'),
        'apr_real_time': fields.float('Apr Real Time'),
        'may_real_time': fields.float('May Real Time'),
        'jun_real_time': fields.float('Jun Real Time'),
        'jul_real_time': fields.float('Jul Real Time'),
        'aug_real_time': fields.float('Aug Real Time'),
        'sep_real_time': fields.float('Sep Real Time'),
        'oct_real_time': fields.float('Oct Real Time'),
        'nov_real_time': fields.float('Nov Real Time'),
        'dec_real_time': fields.float('Dec Real Time'),
        'total_real_time': fields.function(_get_total_real_time, type="float", digits=(16,2), string="Total Real Time", readonly=True, store=True),
    }
    
    _defaults = {
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'mrp.forecast.line') or '/'
    }
mrp_forecast_line()
