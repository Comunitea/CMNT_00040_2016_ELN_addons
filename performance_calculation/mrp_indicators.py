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
from osv import osv, fields
import decimal_precision as dp

class mrp_indicators(osv.osv):
    _name = 'mrp.indicators'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'line_ids': fields.one2many('mrp.indicators.line', 'indicator_id', 'Lines'),
        'line_average_ids': fields.one2many('mrp.indicators.averages', 'indicator_id', 'Averages'),
        'date': fields.date('Date'),
        'user_id': fields.many2one('res.users', 'User'),
        'company_id': fields.many2one('res.company', 'Company'),
        'report_name': fields.char('Report', size=255)
    }
mrp_indicators()

class mrp_indicators_line(osv.osv):
    _name = 'mrp.indicators.line'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'date': fields.date('Date'),
        'workcenter_id': fields.many2one('mrp.workcenter', 'Workcenter'),
        'qty': fields.float('Qty', digits_compute=dp.get_precision('Product UoM'), required=True),
        'qty_scraps': fields.float('Scraps', digits_compute=dp.get_precision('Product UoM')),
        'qty_good': fields.float('Real qty', digits_compute=dp.get_precision('Product UoM')),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'stop_time': fields.float('Stop time'),
        'real_time': fields.float('Real time'),
        'tic_time': fields.float('TiC time'),
        'time_start': fields.float('Time start'),
        'time_stop': fields.float('Time stop'),
        'gasoleo_start': fields.float('Gasoleo start'),
        'gasoleo_stop': fields.float('Gasoleo stop'),
        'oee': fields.float('OEE'),
        'availability': fields.float('Availability'),
        'performance': fields.float('Performance'),
        'quality': fields.float('Quality'),
        'indicator_id': fields.many2one('mrp.indicators', 'Indicator', required=True)
    }
mrp_indicators_line()

class mrp_indicators_averages(osv.osv):
    _name = 'mrp.indicators.averages'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'oee': fields.float('OEE'),
        'availability': fields.float('Availability'),
        'performance': fields.float('Performance'),
        'quality': fields.float('Quality'),
        'indicator_id': fields.many2one('mrp.indicators', 'Incicator', required=True)
    }
mrp_indicators_averages()

class mrp_indicators_scrap(osv.osv):

    _name = 'mrp.indicators.scrap'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'line_ids': fields.one2many('mrp.indicators.scrap.line', 'indicator_id', 'Lines'),
        'date': fields.date('Date'),
        'user_id': fields.many2one('res.users', 'User'),
        'company_id': fields.many2one('res.company', 'Company'),
        'report_name': fields.char('Report', size=255)
    }

mrp_indicators_scrap()

class mrp_indicators_scrap_line(osv.osv):

    _name = 'mrp.indicators.scrap.line'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'date': fields.date('Date'),
        'production_id': fields.many2one('mrp.production', 'Production', select=True),
        'product_id': fields.many2one('product.product', 'Product', select=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure'),
        'real_qty': fields.float('Real qty.', digits_compute=dp.get_precision('Product UoM')),
        'theorical_qty':fields.float('Total qty.', digits_compute=dp.get_precision('Product UoM')),
        'scrap_qty': fields.float('Scrap qty.', digits_compute=dp.get_precision('Product UoM')),
        'real_cost': fields.float('Real cost', digits_compute=dp.get_precision('Product UoM')),
        'theorical_cost': fields.float('Theorical cost', digits_compute=dp.get_precision('Product UoM')),
        'scrap_cost': fields.float('Scrap', digits_compute=dp.get_precision('Product UoM'), select=True),
        'usage_cost': fields.float('Usage', digits_compute=dp.get_precision('Product UoM'), select=True),
        'indicator_id': fields.many2one('mrp.indicators.scrap', 'Indicator', required=True),
    }

mrp_indicators_scrap_line()
