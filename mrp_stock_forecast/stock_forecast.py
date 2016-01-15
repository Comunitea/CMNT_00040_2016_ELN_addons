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
from openerp.osv import osv, fields
import time
from openerp import netsvc
from openerp.tools.translate import _

class forecast_kg_sold(osv.osv):
    _name = 'forecast.kg.sold'
    _description = 'Forecast of kg moved'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'analytic_id': fields.many2one('account.analytic.account', 'Account',
                                        ),
        'commercial_id': fields.many2one('res.users', 'Commercial'),
        'date': fields.date('Date'),
        'kgsold_forecast_lines': fields.one2many('forecast.kg.sold.line',
                                                'kgsold_forecast_id', 'Lines'),
        'company_id': fields.many2one('res.company', 'Company'),
        'state': fields.selection([
                                ('draft','Draft'),
                                ('approve', 'Approved'),
                                ('cancel', 'Cancel')], string="State",
                                required=True, readonly=True),
        'year': fields.integer('Year', size=4),
        'merged_into_id': fields.many2one('forecast.kg.sold', 'Merged into', required=False, readonly=True),
        'merged_from_ids': fields.one2many('forecast.kg.sold', 'merged_into_id', 'Merged from', readonly=True),
    }

    _defaults = {
        'state': 'draft',
        'commercial_id': lambda obj, cr, uid, context: uid,
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
        forecast_obj = self.pool.get('forecast.kg.sold')
        forecast_line_obj = self.pool.get('forecast.kg.sold.line')

        old_ids = []
        res = {}
        lines = []
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id and self.pool.get('res.users').browse(cr, uid, uid).company_id.id or False
        new_id = forecast_obj.create(cr, uid, {'name': _('Stock forecast MERGED. '),
                                                   #~ 'analytic_id': cur.analytic_id.id,
                                                   'commercial_id': uid,
                                                   'date': time.strftime('%d-%m-%Y'),
                                                   'company_id': company,
                                                   'state': 'draft'
                                                    })

        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        for porder in self.browse(cr, uid, ids, context=context):
            forecast_obj.write(cr, uid, porder.id,{'merged_into_id': new_id})
            old_ids.append(porder.id)
            for l in porder.kgsold_forecast_lines:
                lines.append(l.id)
        if lines:
            for line in forecast_line_obj.browse(cr, uid, lines):
                if not res.get(line.format_id.id):
                    res[line.format_id.id] = {}
                for month in range(0,12):
                    if not res[line.format_id.id].get(months[month] + '_kg'):
                        res[line.format_id.id][months[month] + '_kg'] = 0.0
                    res[line.format_id.id][months[month] + '_kg'] = res[line.format_id.id][months[month] + '_kg'] + (eval('o.' + (months[month] + '_kg'),{'o': line}))


        #res = {product_id:{'ene_qty': 100.00, 'feb_qty':2500.00}}
        if res:
            for product in res:
                nwline = forecast_line_obj.create(cr, uid, {
                                'kgsold_forecast_id': new_id,

                                'format_id': product})
                for month in range(0,12):
                    forecast_line_obj.write(cr, uid, nwline, {
                               months[month] + '_kg': res[product][months[month] + '_kg']})


            # make triggers pointing to the old purchases forecast to the new forecast
        if old_ids:
            for old_id in old_ids:
                wf_service.trg_validate(uid, 'forecast.kg.sold', old_id, 'action_cancel', cr)
        return new_id

forecast_kg_sold()

class forecast_kg_sold_line(osv.osv):
    _name = 'forecast.kg.sold.line'
    def _get_total_kg(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.jan_kg + line.feb_kg + line.mar_kg + \
                           line.apr_kg + line.may_kg + line.jun_kg + \
                           line.jul_kg + line.aug_kg + line.sep_kg + \
                           line.oct_kg + line.nov_kg + line.dec_kg
        return res

    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'kgsold_forecast_id': fields.many2one('forecast.kg.sold', 'Forecast kg sold',
                                                required=True, ondelete='cascade'),
        'format_id': fields.many2one('product.format',
                                        'Product Format'),
        'notes': fields.char('Notes', size=32),
        'jan_kg': fields.float('Jan Kg'),
        'feb_kg': fields.float('Feb Kg'),
        'mar_kg': fields.float('Mar Kg'),
        'apr_kg': fields.float('Apr Kg'),
        'may_kg': fields.float('May Kg'),
        'jun_kg': fields.float('Jun Kg'),
        'jul_kg': fields.float('Jul Kg'),
        'aug_kg': fields.float('Aug Kg'),
        'sep_kg': fields.float('Sep Kg'),
        'oct_kg': fields.float('Oct Kg'),
        'nov_kg': fields.float('Nov Kg'),
        'dec_kg': fields.float('Dec Kg'),
        'total_kg': fields.function(_get_total_kg, type="float",
                                    digits=(16,2), string="Total €", readonly=True, store=True),

    }
    _defaults = {
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'forecast.kg.sold.line') or '/'
    }
forecast_kg_sold_line()
