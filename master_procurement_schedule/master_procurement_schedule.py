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
import time
import calendar
from openerp.osv import osv, fields
from openerp import netsvc
from openerp.tools.translate import _
import logging

MONTHS = [('0','January'), ('1','February'), ('2','March'),
          ('3','April'), ('4','May'), ('5','June'),
          ('6','July'), ('7','August'), ('8','September'),
          ('9','October'), ('10','November'), ('11','December')]

_logger = logging.getLogger('mps')

def rounding(fl, round_value):
    if not round_value:
        return fl
    return round(fl / round_value) * round_value

class stock_plannings(osv.osv):
    _name = "stock.plannings"

    def _get_past_future(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        for val in self.browse(cr, uid, ids, context=context):
            if val.date < time.strftime('%Y-%m-%d'):
                res[val.id] = 'Past'
            else:
                res[val.id] = 'Future'
        return res

    def _get_op(self, cr, uid, ids, field_names, arg, context=None):  # op = OrderPoint
        res = {}
        for val in self.browse(cr, uid, ids, context=context):
            res[val.id]={}
            cr.execute("SELECT product_min_qty, product_max_qty, product_uom  \
                        FROM stock_warehouse_orderpoint \
                        WHERE warehouse_id = %s AND product_id = %s AND active = 'TRUE'", (val.warehouse_id.id, val.product_id.id))
            ret = cr.fetchone() or [0.0,0.0,False]
            coef = 1
            round_value = 1
            if ret[2]:
                coef = self._to_default_uom_factor(cr, uid, val.product_id.id, ret[2], context)
                res_coef, round_value = self._from_default_uom_factor(cr, uid, val.product_id.id, val.product_uom.id, context=context)
                coef = coef * res_coef
            res[val.id]['minimum_op'] = rounding(ret[0]*coef, round_value)
            res[val.id]['maximum_op'] = rounding(ret[1]*coef, round_value)
        return res

    _rec_name = 'product_id'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required = True),
        'history': fields.text('Procurement History', readonly=True, help = "History of procurement or internal supply of this planningss line."),
        'state' : fields.selection([('draft','Draft'),('done','Done')],'State',readonly=True),
        'period_id': fields.selection(MONTHS,'Period'),
        'warehouse_id': fields.many2one('stock.warehouse','Warehouse', required=True),
        'product_id': fields.many2one('product.product' , 'Product', required=True, help = 'Product which this planningss is created for.'),
        'product_uom_categ' : fields.many2one('product.uom.categ', 'Product UoM Category'), # Invisible field for product_uom domain
        'product_uom': fields.many2one('product.uom', 'UoM', required=True, help = "Unit of Measure used to show the quantities of stock calculation." \
                        "You can use units from default category or from second category (UoS category)."),
        'product_uos_categ': fields.many2one('product.uom.categ', 'Product UoM Category'), # Invisible field for product_uos domain
        'active_uom': fields.many2one('product.uom',  string = "Active UoM"), #  It works only in Forecast
        'planned_outgoing': fields.float('Planned Out', required=True,  \
                help = 'Enter planned outgoing quantity from selected Warehouse during the selected Period of selected Product. '\
                        'To plan this value look at Confirmed Out or Sales Forecasts. This value should be equal or greater than Confirmed Out.'),
        'date': fields.date('Date'),
        'stock_simulation': fields.float('Stock Simulation', readonly =True, \
                help = 'Stock simulation at the end of selected Period.\n For current period it is: \n' \
                       'Initial Stock - Already Out + Already In - Expected Out + Incoming Left.\n' \
                        'For periods ahead it is: \nInitial Stock - Planned Out Before + Incoming Before - Planned Out + Planned In.'),
        'incoming': fields.float('Confirmed In', readonly=True, \
                help = 'Quantity of all confirmed incoming moves in calculated Period.'),
        'outgoing': fields.float('Confirmed Out', readonly=True, \
                help = 'Quantity of all confirmed outgoing moves in calculated Period.'),
        'incoming_left': fields.float('Incoming Left', readonly=True,  \
                help = 'Quantity left to Planned incoming quantity. This is calculated difference between Planned In and Confirmed In. ' \
                        'For current period Already In is also calculated. This value is used to create procurement for lacking quantity.'),
        'outgoing_left': fields.float('Expected Out', readonly=True, \
                help = 'Quantity expected to go out in selected period besides Confirmed Out. As a difference between Planned Out and Confirmed Out. ' \
                        'For current period Already Out is also calculated'),
        'to_procure': fields.float(string='Planned In', required=True, \
                help = 'Enter quantity which (by your plan) should come in. Change this value and observe Stock simulation. ' \
                        'This value should be equal or greater than Confirmed In.'),
        'line_time': fields.function(_get_past_future, type='char', string='Past/Future'),
        # 'minimum_op': fields.function(_get_op, type='float', string = 'Minimum Rule', multi= 'minimum', \
        #                     help = 'Minimum quantity set in Minimum Stock Rules for this Warehouse'),
        # 'maximum_op': fields.function(_get_op, type='float', string = 'Maximum Rule', multi= 'maximum', \
        #                     help = 'Maximum quantity set in Minimum Stock Rules for this Warehouse'),
        'outgoing_before': fields.float('Planned Out Before', readonly=True, \
                            help= 'Planned Out in periods before calculated. '\
                                    'Between start date of current period and one day before start of calculated period.'),
        'incoming_before': fields.float('Incoming Before', readonly = True, \
                            help= 'Confirmed incoming in periods before calculated (Including Already In). '\
                                    'Between start date of current period and one day before start of calculated period.'),
        'stock_start': fields.float('Initial Stock', readonly=True, \
                            help= 'Stock quantity one day before current period.'),
        'already_out': fields.float('Already Out', readonly=True, \
                            help= 'Quantity which is already dispatched out of this warehouse in current period.'),
        'already_in': fields.float('Already In', readonly=True, \
                            help= 'Quantity which is already picked up to this warehouse in current period.'),
        'stock_only': fields.boolean("Stock Location Only", help = "Check to calculate stock location of selected warehouse only. " \
                                        "If not selected calculation is made for input, stock and output location of warehouse."),
        "procure_to_stock": fields.boolean("Procure To Stock Location", help = "Check to make procurement to stock location of selected warehouse. " \
                                        "If not selected procurement will be made into input location of warehouse."),
        "confirmed_forecasts_only": fields.boolean("Validated Forecasts", help = "Check to take validated forecasts only. " \
                    "If not checked system takes validated and draft forecasts."),
        'supply_warehouse_id': fields.many2one('stock.warehouse','Source Warehouse', help = "Warehouse used as source in supply pick move created by 'Supply from Another Warehouse'."),
        "stock_supply_location": fields.boolean("Stock Supply Location", help = "Check to supply from Stock location of Supply Warehouse. " \
                "If not checked supply will be made from Output location of Supply Warehouse. Used in 'Supply from Another Warehouse' with Supply Warehouse."),
    }

    _defaults = {
        'state': 'draft' ,
        'to_procure': 0.0,
        'planned_outgoing': 0.0,
        'date': time.strftime("%Y-%m-%d"),
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'stock.planningss', context=c),
    }

    _order = 'date'
    
    def _from_default_uom_factor(self, cr, uid, product_id, uom_id, context=None):
        uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        product = product_obj.browse(cr, uid, product_id, context=context)
        uom = uom_obj.browse(cr, uid, uom_id, context=context)
        res = uom.factor
        if uom.category_id.id != product.uom_id.category_id.id:
            res = res * product.uos_coeff
        return res / product.uom_id.factor, uom.rounding
    
    def _to_default_uom_factor(self, cr, uid, product_id, uom_id, context=None):
        uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        product = product_obj.browse(cr, uid, product_id, context=context)
        uom = uom_obj.browse(cr, uid, uom_id, context=context)
        coef = uom.factor
        if uom.category_id.id != product.uom_id.category_id.id:
            coef = coef * product.uos_coeff
        return product.uom_id.factor / coef

    def _to_default_uom(self, cr, uid, val, qtys, context=None):
        res_qty = 0
        if qtys:
            for qty, prod_uom in qtys:
                coef = self._to_default_uom_factor(cr, uid, val.product_id.id, prod_uom, context=context)
                res_qty += qty * coef
        return res_qty

    def onchange_company(self, cr, uid, ids, company_id=False):
        result = {}
        if company_id:
            result['warehouse_id'] = False
        return {'value': result}

    def onchange_uom(self, cr, uid, ids, product_uom=False, product_id=False, active_uom=False,
                     planned_outgoing=0.0, to_procure=0.0):
        ret = {}
        if not product_uom:
            return {}
        if active_uom:
            coeff_uom2def = self._to_default_uom_factor(cr, uid, product_id, active_uom, {})
            coeff_def2uom, round_value = self._from_default_uom_factor(cr, uid, product_id, product_uom, {})
            coeff = coeff_uom2def * coeff_def2uom
            ret['planned_outgoing'] = rounding(coeff * planned_outgoing, round_value)
            ret['to_procure'] = rounding(coeff * to_procure, round_value)
        ret['active_uom'] = product_uom
        return {'value': ret}

    def product_id_change(self, cr, uid, ids, product_id):
        ret = {}
        if product_id:
            product_rec =  self.pool.get('product.product').browse(cr, uid, product_id)
            ret['product_uom'] = product_rec.uom_id.id
            ret['active_uom'] = product_rec.uom_id.id
            ret['product_uom_categ'] = product_rec.uom_id.category_id.id
            ret['product_uos_categ'] = product_rec.uos_id and product_rec.uos_id.category_id.id or False
        else:
            ret['product_uom'] = False
            ret['product_uom_categ'] = False
            ret['product_uos_categ'] = False
        res = {'value': ret}
        return res

    def _get_in_out(self, cr, uid, val, date_start, date_stop, direction, done, context=None):
        if context is None:
            context = {}
        product_obj = self.pool.get('product.product')
        mapping = {'in': {
                        'field': "incoming_qty",
                        'adapter': lambda x: x,
                  },
                  'out': {
                        'field': "outgoing_qty",
                        'adapter': lambda x: -x,
                  },
        }
        context['from_date'] = date_start
        context['to_date'] = date_stop
        locations = [val.warehouse_id.lot_stock_id.id,]
        if not val.stock_only:
            locations.extend([val.warehouse_id.lot_input_id.id, val.warehouse_id.lot_output_id.id])
        context['location'] = locations
        context['compute_child'] = True
        prod_id = val.product_id.id
        if done:
            context.update({ 'states':('done',), 'what':(direction,) })
            prod_ids = [prod_id]
            st = product_obj.get_product_available(cr, uid, prod_ids, context=context)
            res = mapping[direction]['adapter'](st.get(prod_id,0.0))
        else:
            product = product_obj.read(cr, uid, prod_id,[], context)
            product_qty = product[mapping[direction]['field']]
            res = mapping[direction]['adapter'](product_qty)
        return res

    def _get_outgoing_before(self, cr, uid, val, date_start, date_stop, context=None):
        cr.execute("SELECT sum(plannings.planned_outgoing), plannings.product_uom \
                    FROM stock_plannings AS plannings \
                    WHERE (plannings.date >= %s) AND (plannings.date <= %s) \
                        AND (plannings.product_id = %s) AND (plannings.company_id = %s) \
                    GROUP BY plannings.product_uom", \
                        (date_start, date_stop, val.product_id.id, val.company_id.id,))
        plannings_qtys = cr.fetchall()
        res = self._to_default_uom(cr, uid, val, plannings_qtys, context)
        return res

    def _get_stock_start(self, cr, uid, val, date, context=None):
        if context is None:
            context = {}
        context['from_date'] = None
        context['to_date'] = date
        locations = [val.warehouse_id.lot_stock_id.id,]
        if not val.stock_only:
            locations.extend([val.warehouse_id.lot_input_id.id, val.warehouse_id.lot_output_id.id])
        context['location'] = locations
        context['compute_child'] = True
        product_obj =  self.pool.get('product.product').read(cr, uid,val.product_id.id,[], context)
        res = product_obj['qty_available']     # value for stock_start
        return res

    def calculate_plannings(self, cr, uid, ids, context, *args):
#        one_second = relativedelta(seconds=1)
#        today = datetime.today()
#        current_date_beginning_c = datetime(today.year, today.month, today.day)
#        current_date_end_c = current_date_beginning_c  + relativedelta(days=1, seconds=-1)  # to get hour 23:59:59
#        current_date_beginning = current_date_beginning_c.strftime('%Y-%m-%d %H:%M:%S')
#        current_date_end = current_date_end_c.strftime('%Y-%m-%d %H:%M:%S')
#        _logger.debug("Calculate plannings: current date beg: %s and end: %s", current_date_beginning, current_date_end)
        for val in self.browse(cr, uid, ids, context=context):
            year = val.date[:4]
            month = str(int(val.period_id)+1)
            first_day, last_day = calendar.monthrange(int(year),int(month))
            last_date = year+"-"+month+"-"+str(last_day)
            first_date = year+"-"+month+"-"+str(first_day)
            complet_last_date = year+"-"+month+"-"+str(last_day) + " 00:00:00"
            complet_first_date = year+"-"+month+"-"+str(first_day) + " 23:59:59"
            
#            day = datetime.strptime(val.date + " 00:00:00", '%Y-%m-%d %H:%M:%S')
#            dbefore = datetime(day.year, day.month, day.day) - one_second
#            day_before_calculated_period = dbefore.strftime('%Y-%m-%d %H:%M:%S')   # one day before start of calculated period
#            _logger.debug("Day before calculated period: %s ", day_before_calculated_period)
#            cr.execute("SELECT date_start \
#                    FROM stock_period AS period \
#                    LEFT JOIN stock_plannings AS plannings \
#                    ON (plannings.period_id = period.id) \
#                    WHERE (period.date_stop >= %s) AND (period.date_start <= %s) AND \
#                        plannings.product_id = %s", (current_date_end, current_date_end, val.product_id.id,)) #
#            date = cr.fetchone()
#            start_date_current_period = date and date[0] or False
#            start_date_current_period = start_date_current_period or current_date_beginning
#            day = datetime.strptime(start_date_current_period, '%Y-%m-%d %H:%M:%S')
#            dbefore = datetime(day.year, day.month, day.day) - one_second
#            date_for_start = dbefore.strftime('%Y-%m-%d %H:%M:%S')   # one day before current period
#            _logger.debug("Date for start: %s", date_for_start)
#
            
            
            
            already_out = self._get_in_out(cr, uid, val, complet_first_date, complet_last_date, direction='out', done=True, context=context),
            already_in = self._get_in_out(cr, uid, val, complet_first_date, complet_last_date, direction='in', done=True, context=context),
            outgoing = self._get_in_out(cr, uid, val, complet_first_date, complet_last_date, direction='out', done=False, context=context),
            #TODO ¡¡¡¡¡¡Period_id por fecha y mes!!!!!!!!!!!!!!!!!!!! #TODO
            incoming = self._get_in_out(cr, uid, val, first_date,complet_last_date, direction='in', done=False, context=context),
            outgoing_before = self._get_outgoing_before(cr, uid, val, complet_first_date, complet_last_date, context=context),
            incoming_before = self._get_in_out(cr, uid, val, complet_first_date, complet_last_date, direction='in', done=False, context=context),
            stock_start = self._get_stock_start(cr, uid, val, complet_first_date, context=context),
            if time.strftime('%Y-%m-%d %H:%M:%S') == complet_first_date:   # current period is calculated
                current = True
            else:
                current = False
            factor, round_value = self._from_default_uom_factor(cr, uid, val.product_id.id, val.product_uom.id, context=context)
            self.write(cr, uid, ids, {
                'already_out': rounding(already_out[0]*factor,round_value),
                'already_in': rounding(already_in[0]*factor,round_value),
                'outgoing': rounding(outgoing[0]*factor,round_value),
                'incoming': rounding(incoming[0]*factor,round_value),
                'outgoing_before' : rounding(outgoing_before[0]*factor,round_value),
                'incoming_before': rounding((incoming_before[0]+ (not current and already_in[0]))*factor,round_value),
                'outgoing_left': rounding(val.planned_outgoing - (outgoing[0] + (current and already_out[0]))*factor,round_value),
                'incoming_left': rounding(val.to_procure - (incoming[0] + (current and already_in[0]))*factor,round_value),
                'stock_start': rounding(stock_start[0]*factor,round_value),
                'stock_simulation': rounding(val.to_procure - val.planned_outgoing + (stock_start[0]+ incoming_before[0] - outgoing_before[0] \
                                     + (not current and already_in[0]))*factor,round_value),
            })
        return True

# method below converts quantities and uoms to general OpenERP standard with UoM Qty, UoM, UoS Qty, UoS.
# from stock_plannings standard where you have one Qty and one UoM (any from UoM or UoS category)
# so if UoM is from UoM category it is used as UoM in standard and if product has UoS the UoS will be calcualated.
# If UoM is from UoS category it is recalculated to basic UoS from product (in plannings you can use any UoS from UoS category)
# and basic UoM is calculated.
    def _qty_to_standard(self, cr, uid, val, context=None):
        uos = False
        uos_qty = 0.0
        if val.product_uom.category_id.id == val.product_id.uom_id.category_id.id:
            uom_qty = val.incoming_left
            uom = val.product_uom.id
            if val.product_id.uos_id:
                uos = val.product_id.uos_id.id
                coeff_uom2def = self._to_default_uom_factor(cr, uid, val.product_id.id, val.product_uom.id, {})
                coeff_def2uom, round_value = self._from_default_uom_factor(cr, uid, val.product_id.id, uos, {})
                uos_qty = rounding(val.incoming_left * coeff_uom2def * coeff_def2uom, round_value)
        elif val.product_uom.category_id.id == val.product_id.uos_id.category_id.id:
            coeff_uom2def = self._to_default_uom_factor(cr, uid, val.product_id.id, val.product_uom.id, {})
            uos = val.product_id.uos_id.id
            coeff_def2uom, round_value = self._from_default_uom_factor(cr, uid, val.product_id.id, uos, {})
            uos_qty = rounding(val.incoming_left * coeff_uom2def * coeff_def2uom, round_value)
            uom = val.product_id.uom_id.id
            coeff_def2uom, round_value = self._from_default_uom_factor(cr, uid, val.product_id.id, uom, {})
            uom_qty = rounding(val.incoming_left * coeff_uom2def * coeff_def2uom, round_value)
        return uom_qty, uom, uos_qty, uos

    def procure_incomming_left(self, cr, uid, ids, context, *args):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.incoming_left <= 0:
                raise osv.except_osv(_('Error !'), _('Incoming Left must be greater than 0 !'))
            uom_qty, uom, uos_qty, uos = self._qty_to_standard(cr, uid, obj, context)
            user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            proc_id = self.pool.get('procurement.order').create(cr, uid, {
                        'company_id' : obj.company_id.id,
                        'name': _('MPS plannings for %s') %(obj.date),
                        'origin': _('MPS(%s) %s') %(user.login, obj.date),
                        'date_planned': obj.date + "00:00:00",
                        'product_id': obj.product_id.id,
                        'product_qty': uom_qty,
                        'product_uom': uom,
                        'product_uos_qty': uos_qty,
                        'product_uos': uos,
                        'location_id': obj.procure_to_stock and obj.warehouse_id.lot_stock_id.id or obj.warehouse_id.lot_input_id.id,
                        'procure_method': 'make_to_order',
                        'note' : _(' Procurement created by MPS for user: %s   Creation Date: %s \
                                        \n For period: %s \
                                        \n according to state: \
                                        \n Warehouse Forecast: %s \
                                        \n Initial Stock: %s \
                                        \n Planned Out: %s    Planned In: %s \
                                        \n Already Out: %s    Already In: %s \
                                        \n Confirmed Out: %s    Confirmed In: %s \
                                        \n Planned Out Before: %s    Confirmed In Before: %s \
                                        \n Expected Out: %s    Incoming Left: %s \
                                        \n Stock Simulation: %s    Minimum stock: %s') %(user.login, time.strftime('%Y-%m-%d %H:%M:%S'),
                                        obj.date, obj.warehouse_forecast, obj.planned_outgoing, obj.stock_start, obj.to_procure,
                                        obj.already_out, obj.already_in, obj.outgoing, obj.incoming, obj.outgoing_before, obj.incoming_before,
                                        obj.outgoing_left, obj.incoming_left, obj.stock_simulation, obj.minimum_op)
                            }, context=context)
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)
            self.calculate_plannings(cr, uid, ids, context)
            prev_text = obj.history or ""
            self.write(cr, uid, ids, {
                    'history': _('%s Procurement (%s,  %s) %s %s \n') % (prev_text, user.login, time.strftime('%Y.%m.%d %H:%M'),
                    obj.incoming_left, obj.product_uom.name)
                })

        return True

    def internal_supply(self, cr, uid, ids, context, *args):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.incoming_left <= 0:
                raise osv.except_osv(_('Error !'), _('Incoming Left must be greater than 0 !'))
            if not obj.supply_warehouse_id:
                raise osv.except_osv(_('Error !'), _('You must specify a Source Warehouse !'))
            if obj.supply_warehouse_id.id == obj.warehouse_id.id:
                raise osv.except_osv(_('Error !'), _('You must specify a Source Warehouse different than calculated (destination) Warehouse !'))
            uom_qty, uom, uos_qty, uos = self._qty_to_standard(cr, uid, obj, context)
            user = self.pool.get('res.users').browse(cr, uid, uid, context)
            picking_id = self.pool.get('stock.picking').create(cr, uid, {
                        'origin': _('MPS(%s) %s') %(user.login, obj.date),
                        'type': 'internal',
                        'state': 'auto',
                        'date': obj.date + " 00:00:00",
                        'move_type': 'direct',
                        'invoice_state':  'none',
                        'company_id': obj.company_id.id,
                        'note': _('Pick created from MPS by user: %s   Creation Date: %s \
                                    \nFor period: %s   according to state: \
                                    \n Warehouse Forecast: %s \
                                    \n Initial Stock: %s \
                                    \n Planned Out: %s  Planned In: %s \
                                    \n Already Out: %s  Already In: %s \
                                    \n Confirmed Out: %s   Confirmed In: %s \
                                    \n Planned Out Before: %s   Confirmed In Before: %s \
                                    \n Expected Out: %s   Incoming Left: %s \
                                    \n Stock Simulation: %s   Minimum stock: %s ')
                                    % (user.login, time.strftime('%Y-%m-%d %H:%M:%S'), obj.date, obj.warehouse_forecast,
                                       obj.stock_start, obj.planned_outgoing, obj.to_procure, obj.already_out, obj.already_in,
                                       obj.outgoing, obj.incoming, obj.outgoing_before, obj.incoming_before,
                                       obj.outgoing_left, obj.incoming_left, obj.stock_simulation, obj.minimum_op)
                        })

            move_id = self.pool.get('stock.move').create(cr, uid, {
                        'name': _('MPS(%s) %s') %(user.login, obj.date),
                        'picking_id': picking_id,
                        'product_id': obj.product_id.id,
                        'date': obj.date,
                        'product_qty': uom_qty,
                        'product_uom': uom,
                        'product_uos_qty': uos_qty,
                        'product_uos': uos,
                        'location_id': obj.stock_supply_location and obj.supply_warehouse_id.lot_stock_id.id or \
                                                                obj.supply_warehouse_id.lot_output_id.id,
                        'location_dest_id': obj.procure_to_stock and obj.warehouse_id.lot_stock_id.id or \
                                                                obj.warehouse_id.lot_input_id.id,
                        'tracking_id': False,
                        'company_id': obj.company_id.id,
                    })
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)

        self.calculate_plannings(cr, uid, ids, context)
        prev_text = obj.history or ""
        pick_name = self.pool.get('stock.picking').browse(cr, uid, picking_id).name
        self.write(cr, uid, ids, {
                    'history': _('%s Pick List %s (%s,  %s) %s %s \n') % (prev_text, pick_name, user.login, time.strftime('%Y.%m.%d %H:%M'),
                    obj.incoming_left, obj.product_uom.name)
                })

        return True

    

stock_plannings()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
