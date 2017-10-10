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
from openerp.osv import orm, fields
import time
from datetime import datetime
from openerp.tools.translate import _


class performance_calculation(orm.TransientModel):
    _name = 'performance.calculation'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'report_type': fields.selection([
            ('oee', "OEE"),
            ('availability', 'Availability'),
            ('performance', 'Performance'),
            ('quality','Quality'),
            ('scrap_and_usage', 'Scrap & Usage')
           ], 'Report type', required=True),
        'between_dates': fields.boolean('Between dates'),
        'date_start': fields.date('Date start'),
        'date_stop': fields.date('Date stop'),
        'by_routing': fields.boolean('By routing'),
        'routing_id': fields.many2one('mrp.routing', 'Routing'),
        'by_product': fields.boolean('By product'),
        'product_id': fields.many2one('product.product', 'Product'),
        'by_workcenter_id': fields.boolean('By workcenter'),
        'workcenter_id': fields.many2one('mrp.workcenter', 'Workcenter')
    }

    def _get_moves_by_filters(self, cr, uid, ids, context=None):
        result = []
        domain = [('production_state','=','done'), ('production_type','=','normal')]

        form = self.browse(cr, uid, ids[0], context)

        if form.date_start and form.date_stop:
            domain.append(('date_start','>=',form.date_start))
            domain.append(('date_start','<=',form.date_stop))
            domain.append(('date_finished','<=',form.date_stop))
            domain.append(('date_finished','>=',form.date_start))
        if form.routing_id:
            domain.append(('routing_id','=',form.routing_id.id))
        if form.product_id:
            domain.append(('product','=',form.product_id.id))
        if form.workcenter_id:
            domain.append(('workcenter_id','=',form.workcenter_id.id))

        result = self.pool.get('mrp.production.workcenter.line').search(cr, uid, domain)

        return result

    def _get_name_by_filters(self, cr, uid, ids, context=None):
        report_name_comp = ''

        for form in self.browse(cr, uid, ids, context):

            if form.between_dates:
                report_name_comp += _(" From: ") + form.date_start + _(" to: ") + form.date_stop

            if form.by_routing:
                report_name_comp += _(" Routing: ") + form.routing_id.name

            if form.by_product:
                report_name_comp += _(" Product: ") + form.product_id.name

            if form.by_workcenter_id:
                report_name_comp += _(" Workcenter: ") + form.workcenter_id.name

        return report_name_comp

    def _get_total_stop_time(self, cr, uid, ids, obj, context=None):
        stop_time = 0.0

        minimum_time = 2.0 / 60.0 # 2 minutes (las iguales o inferiores a este tiempo no se computan)
        for stop in obj.production_stops_ids.filtered(lambda r: r.time > minimum_time):
            stop_time += stop.time

        return stop_time

    def _get_total_qty(self, cr, uid, ids, obj, context=None):
        qty_finished = 0.0
        qty_real_finished = 0.0
        qty_scrap = 0.0

        moves = self.pool.get('stock.move').search(cr, uid, [('production_id','=',obj.production_id.id), ('state','=','done')])
        for move in self.pool.get('stock.move').browse(cr, uid, moves):
            if not move.scrapped or (move.scrapped and move.location_id.usage == 'production'):
                qty_finished += move.product_uom_qty
            if move.scrapped:
                qty_scrap += move.product_uom_qty
            if not move.scrapped:
                qty_real_finished += move.product_uom_qty
            elif move.location_id.usage == 'internal':
                qty_real_finished -= move.product_uom_qty

        return qty_finished, qty_real_finished, qty_scrap

    def _get_availability(self, cr, uid, ids, stop_time=0.0, estimated_time=0.0, time_cycle=0.0, qty_cycle=0.0, factor=0.0, context=None):
        #Availability = [(Tiempo x ciclo / Qty x ciclo)*Qty a fabricar] /
        #               [((Tiempo x ciclo/Qty x ciclo)*Qty a fabricar) +
        #               Stops + Time after + Time before] * 100
        a = time_cycle / (qty_cycle or 1.0)
        b = (a * factor) + stop_time

        return (estimated_time / (b or 1.0 ))

    def _get_performance(self, cr, uid, ids, estimated_time=0.0, real_time=0.0, context=None):
        #Efficiency / Performance = [(Tiempo x ciclo / Qty x ciclo) * Qty a fabricar] /
        #                           [Real time - Stops] * 100
        return (estimated_time / (real_time or 1.0))

    def _get_quality(self, cr, uid, ids, total_qty=0.0, scrap_qty=0.0, context=None):
        #Quality = ((Total qty - Scraps qty) / Total qty) * 100
        return ((total_qty - scrap_qty) / (total_qty or 1.0))

    def _get_oee(self, cr, uid, ids, estimated_time=0.0, time_cycle=0.0, qty_cycle=0.0, factor=0.0, stop_time=0.0, real_time=0.0, total_qty=0.0, qty_scrap=0.0, context=None):
        #OEE = (Availability * Efficiency * Quality) * 100
        a = self._get_availability(cr, uid, ids, stop_time, estimated_time, time_cycle, qty_cycle, factor, context=context)
        p = self._get_performance(cr, uid, ids, estimated_time, real_time, context=context)
        q = self._get_quality(cr, uid, ids, total_qty, qty_scrap, context=context)
        oee = (a * p * q) * 100
        return (a*100), (p*100), (q*100), oee

    def _get_total_availability(self, cr, uid, ids, stop_time=0.0, estimated_time=0.0, time_cycle=0.0, qty_cycle=0.0, factor=0.0, context=None):
        return (estimated_time / (((time_cycle / (qty_cycle or 1.0)) * factor) + stop_time) or 1.0 )

    def _get_total_performance(self, cr, uid, ids, estimated_time=0.0, real_time=0.0, context=None):
        return (estimated_time / (real_time or 1.0))

    def _get_total_quality(self, cr, uid, ids, total_qty=0.0, scrap_qty=0.0, context=None):
        return ((total_qty - scrap_qty) / (total_qty or 1.0))

    def _get_total_oee(self, cr, uid, ids, estimated_time=0.0, time_cycle=0.0, qty_cycle=0.0, factor=0.0, stop_time=0.0, real_time=0.0, total_qty=0.0, qty_scrap=0.0, context=None):
        a = self._get_total_availability(cr, uid, ids, stop_time, estimated_time, time_cycle, qty_cycle, factor, context=context)
        p = self._get_total_performance(cr, uid, ids, estimated_time, real_time, context=context)
        q = self._get_total_quality(cr, uid, ids, total_qty, qty_scrap, context=context)
        oee = (a * p * q) * 100
        return (a*100), (p*100), (q*100), oee

    def _prepare_indicator(self, cr, uid, ids, name_report, company_id, context=None):
        form = self.browse(cr, uid, ids[0])
        return {'name': "IND/ " +  form.name + "/ " + time.strftime('%Y-%m-%d %H:%M:%S'),
                'date': time.strftime('%Y-%m-%d'),
                'user_id': uid,
                'company_id': company_id,
                'report_name': form.report_type + " - " + name_report}

    def _prepare_indicator_line(self, cr, uid, ids, obj, stop_time, availability, performance, quality, oee, indicator_id, qty_finished, qty_scrap, context=None):
        form = self.browse(cr, uid, ids[0])
        return {
                'name': "INDL/ " +   form.name + "/ " + time.strftime('%Y-%m-%d %H:%M:%S'),
                'date': obj.date_start and (datetime.strptime(obj.date_start, "%Y-%m-%d %H:%M:%S")).strftime('%Y-%m-%d') or False,
                'workcenter_id': obj.workcenter_id and obj.workcenter_id.id or False,
                'qty': qty_finished,
                'product_id': obj.product and obj.product.id or False,
                'stop_time': stop_time,
                'real_time': obj.real_time,
                'tic_time': qty_finished * obj.hour / obj.qty,
                'gasoleo_start':obj.gasoleo_start,
                'gasoleo_stop': obj.gasoleo_stop,
                'availability': availability ,
                'performance': performance ,
                'quality': quality ,
                'oee': oee,
                'indicator_id': indicator_id,
                'qty_scraps': qty_scrap,
                'qty_good': qty_finished - qty_scrap}

    def _prepare_scrap_indicator_line(self, cr, uid, ids, product_id=False, product_uom=False, qty_finished=0.0, real_qty_finished=0.0,\
        qty_scrap=0.0, theo_cost=0.0, real_cost=0.0, usage=0.0, scrap=0.0, production_id=False, indicator_id=False, context=None):
            form = self.browse(cr, uid, ids[0])
            obj = self.pool.get('mrp.production').browse(cr, uid, production_id)
            return {
                    'name': "SCRAPL/ " +   form.name + "/ " + time.strftime('%Y-%m-%d %H:%M:%S'),
                    'date': obj.date_start and (datetime.strptime(obj.date_start, "%Y-%m-%d %H:%M:%S")).strftime('%Y-%m-%d') or False,
                    'production_id': production_id,
                    'product_id': product_id,
                    'product_uom': product_uom,
                    'real_qty': real_qty_finished,
                    'theorical_qty': qty_finished,
                    'scrap_qty': qty_scrap,
                    'real_cost': real_cost,
                    'theorical_cost': theo_cost,
                    'scrap_cost': scrap,
                    'usage_cost': usage,
                    'indicator_id': indicator_id}

    def _get_productions_by_filters(self, cr, uid, ids, context=None):
        result = []
        result2 = []
        domain = [('state','=','done'), ('production_type','=','normal')]

        form = self.browse(cr, uid, ids[0], context)
        prod_obj = self.pool.get('mrp.production')
        prodwork_line = self.pool.get('mrp.production.workcenter.line')

        if form.date_start and form.date_stop:
            domain.append(('date_start','>=',form.date_start))
            domain.append(('date_start','<=',form.date_stop))
            domain.append(('date_finished','<=',form.date_stop))
            domain.append(('date_finished','>=',form.date_start))
        if form.routing_id:
            domain.append(('routing_id','=',form.routing_id.id))
        if form.product_id:
            domain.append(('product_id','=',form.product_id.id))

        result = prod_obj.search(cr, uid, domain)

        if form.workcenter_id:
            if result:
                result2 = prodwork_line.search(cr, uid, [('production_id','in',result), ('workcenter_id','=',form.workcenter_id.id)])
                result = []
            else:
                result2 = prodwork_line.search(cr, uid, [('workcenter_id','=',form.workcenter_id.id)])
            if result2:
                for obj in prodwork_line.browse(cr, uid, result2):
                    result.append(obj.production_id.id)

        return result

    def _calc_finished_qty(self, cr, uid, ids, context=None):
        qty = 0.0

        for move in self.pool.get('stock.move').browse(cr, uid, ids):
            if move.state != 'done':
                continue
            if not move.scrapped or (move.scrapped and move.location_id.usage == 'production'):
                qty += move.product_uom_qty

        return qty

    def _calc_real_finished_qty(self, cr, uid, ids, context=None):
        qty = 0.0

        for move in self.pool.get('stock.move').browse(cr, uid, ids):
            if move.state != 'done':
                continue
            if not move.scrapped:
                qty += move.product_uom_qty
            elif move.location_id.usage == 'internal':
                qty -= move.product_uom_qty

        return qty

    def _get_theo_cost(self, cr, uid, ids, production, product_uom_qty=0.0, context=None):
        theorical_cost = 0.0
        if production.theo_cost:
            theorical_cost = production.theo_cost * product_uom_qty
        else:
            tmpl_obj = self.pool.get('product.template')
            updated_price = tmpl_obj._calc_price(cr, uid, production.bom_id, test=True,
                                                 context=context)
            theorical_cost = updated_price * product_uom_qty
        return theorical_cost

    def _get_real_cost(self, cr, uid, ids, context=None):
        real_cost = 0.0

        for move in self.pool.get('stock.move').browse(cr, uid, ids):
            if move.state != 'done':
                continue
            if not move.scrapped:
                real_cost += (move.price_unit * move.product_uom_qty)

        return real_cost

    def generate_report_scrap_and_usage(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        indicator_id = False
        prod_obj = self.pool.get('mrp.production')
        company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id and self.pool.get('res.users').browse(cr, uid, uid).company_id.id or False
        for form in self.browse(cr, uid, ids, context):
            name_report = self._get_name_by_filters(cr, uid, [form.id], context=context)
            production_ids = self._get_productions_by_filters(cr, uid, ids, context=context)
            if production_ids:
                indicator_id = self.pool.get('mrp.indicators.scrap').create(cr, uid, self._prepare_indicator(cr, uid, ids, name_report, company_id, context=context))
                if indicator_id:
                    for prod in prod_obj.browse(cr, uid, production_ids):
                        ###########################################################
                        qty_finished = 0.0
                        real_qty_finished = 0.0
                        qty_scrap = 0.0
                        theo_cost = 0.0
                        real_cost = 0.0
                        usage = 0.0
                        scrap = 0.0
                        ###########################################################
                        qty_finished = self._calc_finished_qty(cr, uid, [x.id for x in prod.move_created_ids2], context=context)
                        real_qty_finished = self._calc_real_finished_qty(cr, uid, [x.id for x in prod.move_created_ids2], context=context)
                        qty_scrap = qty_finished - real_qty_finished
                        theo_cost = self._get_theo_cost(cr, uid, ids, prod, qty_finished, context=context)
                        real_cost = self._get_real_cost(cr, uid, [x.id for x in prod.move_lines2], context=context)

                        #scrap = (real_cost / (qty_finished or 1.0)) * qty_scrap
                        scrap += qty_scrap * (theo_cost / qty_finished)
                        for move in self.pool.get('stock.move').browse(cr, uid, [x.id for x in prod.move_lines2]):
                            if move.scrapped and move.state != 'cancel':
                                # scrap += (move.product_id.standard_price * move.product_uom_qty)
                                scrap += (move.price_unit * move.product_uom_qty)
                        usage = real_cost - theo_cost
                        real_real_cost = real_cost + scrap

                        self.pool.get('mrp.indicators.scrap.line').create(cr,\
                            uid,self._prepare_scrap_indicator_line(cr,\
                            uid, ids, prod.product_id.id, prod.product_uom.id, qty_finished,\
                            real_qty_finished, qty_scrap, theo_cost, real_real_cost, usage, scrap, prod.id, indicator_id, context=context))
        return indicator_id

    def generate_performance_calculation(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        indicator_id = False
        tot_qty_prod = 0.0
        tot_qty_scrap = 0.0
        tot_estimated_time = 0.0
        tot_factor = 0.0
        tot_qty_cycle = 0.0
        tot_hours_cycle = 0.0

        tot_times_for_availability = 0.0
        tot_times_for_performance = 0.0
        t_oee = 0.0
        t_quality = 0.0
        t_performance = 0.0
        t_availability = 0.0
        company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id and self.pool.get('res.users').browse(cr, uid, uid).company_id.id or False

        for form in self.browse(cr, uid, ids, context):
            if form.report_type == 'scrap_and_usage':

                new_id = self.generate_report_scrap_and_usage(cr, uid, ids, context)

                value = {
                    'domain': str([('id', 'in', [new_id])]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'mrp.indicators.scrap',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'res_id': new_id
                    }
            else:
                name_report = self._get_name_by_filters(cr, uid, [form.id], context=context)
                line_ids = self._get_moves_by_filters(cr, uid, [form.id], context=context)

                if line_ids:
                    indicator_id = self.pool.get('mrp.indicators').create(cr, uid, self._prepare_indicator(cr, uid, ids, name_report, company_id, context=context))
                    for line in line_ids:
                        obj = self.pool.get('mrp.production.workcenter.line').browse(cr, uid, line, context)

                        stop_time = 0.0
                        qty_finished = 0.0
                        qty_real_finished = 0.0
                        qty_scrap = 0
                        availability = 0.0
                        performance = 0.0
                        quality = 0.0
                        oee = 0.0
                        factor = 0.0
                        qty_per_cycle = 0.0
                        estimated_time = 0.0
                        times_for_availability = 0.0
                        times_for_performance = 0.0

                        stop_time = self._get_total_stop_time(cr, uid, ids, obj, context=context)
                        times_for_availability = stop_time + obj.time_start + obj.time_stop
                        times_for_performance = obj.real_time - stop_time
                        qty_finished, qty_real_finished, qty_scrap = self._get_total_qty(cr, uid, ids, obj, context=context)
                        name_routing_workcenter = ((obj.name).split('-')[0])[:-1]

                        routings = self.pool.get('mrp.routing.workcenter').search(cr,
                                                                                uid,
                                                                                [('routing_id', '=', obj.routing_id.id),
                                                                               #('workcenter_id', '=', obj.workcenter_id.id),
                                                                                ('name', 'like', name_routing_workcenter)])
                        if routings:
                            rout = self.pool.get('mrp.routing.workcenter').browse(cr, uid, routings[0])
                            # factor =  self.pool.get('product.uom')._compute_qty(cr, uid, obj.production_id.product_uom.id, obj.production_id.product_qty, obj.production_id.bom_id.product_uom.id)
                            factor = qty_finished
                            qty_per_cycle = self.pool.get('product.uom')._compute_qty(cr, uid, rout.uom_id.id, rout.qty_per_cycle, obj.production_id.bom_id.product_uom.id)
                            estimated_time = float((rout.hour_nbr / (qty_per_cycle or 1.0)) * factor)
                        ########################### TOTALS ###########################
                        tot_qty_scrap += qty_scrap
                        tot_qty_prod += obj.qty
                        tot_hours_cycle += rout.hour_nbr
                        tot_qty_cycle += qty_per_cycle
                        tot_factor += factor
                        tot_estimated_time += estimated_time
                        tot_qty_cycle += qty_per_cycle
                        tot_factor += factor
                        tot_times_for_availability += times_for_availability
                        tot_times_for_performance += times_for_performance
                        ##############################################################

                        if form.report_type == 'availability':
                            availability = (self._get_availability(cr, uid, ids, times_for_availability, estimated_time, rout.hour_nbr, qty_per_cycle, factor, context=context)) * 100

                        if form.report_type == 'performance':
                            performance = (self._get_performance(cr, uid, ids, estimated_time, times_for_performance, context=context)) * 100

                        if form.report_type == 'quality':
                            quality = (self._get_quality(cr, uid, ids, qty_finished, qty_scrap, context=context)) * 100

                        if form.report_type == 'oee':
                            availability, performance, quality, oee = self._get_oee(cr, uid, ids, estimated_time, rout.hour_nbr, qty_per_cycle, factor, times_for_availability, times_for_performance, qty_finished, qty_scrap, context=context)

                        if form.report_type != 'scrap_and_usage':
                            self.pool.get('mrp.indicators.line').create(cr, uid, self._prepare_indicator_line(cr, uid, ids, obj, stop_time, availability, performance, quality, oee, indicator_id, qty_finished, qty_scrap, context=context))

                    if indicator_id:
                        ind = self.pool.get('mrp.indicators').browse(cr, uid, indicator_id)

                        if ind.line_ids:
                            tavailability = 0.0
                            tperformance = 0.0
                            tquality = 0.0
                            toee = 0.0
                            nline = 0

                            for line in ind.line_ids:
                                tavailability += line.availability
                                tperformance += line.performance
                                tquality += line.quality
                                toee += line.oee
                                nline += 1

                            t_availability = tavailability / (nline or 1.0)
                            t_performance = tperformance / (nline or 1.0)
                            t_quality = tquality / (nline or 1.0)
                            t_oee = toee / (nline or 1.0)

                            if form.report_type != 'scrap_and_usage':
                                self.pool.get('mrp.indicators.averages').create(cr,uid, {
                                    'name': "AVG/ " +  form.report_type + "/ " + time.strftime('%Y-%m-%d %H:%M:%S'),
                                    'availability': t_availability,
                                    'performance': t_performance,
                                    'quality': t_quality,
                                    'oee': t_oee,
                                    'indicator_id': indicator_id
                                })

                value = {
                    'domain': str([('id', 'in', [indicator_id])]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'mrp.indicators',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'res_id': indicator_id
                    }

        return value

performance_calculation()
