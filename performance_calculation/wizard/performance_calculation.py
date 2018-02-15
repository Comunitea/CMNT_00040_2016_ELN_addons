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
            ('scrap_and_usage', 'Scrap & Usage'),
            ('overweight', 'Overweight'),
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
        return self.pool.get('mrp.production.workcenter.line').search(cr, uid, domain)

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
        minimum_time = 2.0 / 60.0 # 2 minutos (las iguales o inferiores a este tiempo no se computan)
        for stop in obj.production_stops_ids.filtered(lambda r: r.time > minimum_time):
            stop_time += stop.time
        return stop_time

    def _get_total_qty(self, cr, uid, ids, production, context=None):
        qty_finished = 0.0
        qty_real_finished = 0.0
        qty_scrap = 0.0
        for move in production.move_created_ids2:
            if move.state != 'done':
                continue
            scrapped_move = move.location_dest_id.scrap_location
            if not scrapped_move or (scrapped_move and move.location_id.usage == 'production'):
                qty_finished += move.product_uom_qty
            if scrapped_move:
                qty_scrap += move.product_uom_qty
            if not scrapped_move:
                qty_real_finished += move.product_uom_qty
            elif move.location_id.usage == 'internal':
                qty_real_finished -= move.product_uom_qty
        return qty_finished, qty_real_finished, qty_scrap

    def _get_availability(self, cr, uid, ids, times_for_availability=0.0, estimated_time=0.0, time_cycle=0.0, qty_per_cycle=0.0, factor=0.0, context=None):
        a = time_cycle / (qty_per_cycle or 1.0)
        b = (a * factor) + times_for_availability
        return (estimated_time / (b or 1.0 ))

    def _get_performance(self, cr, uid, ids, estimated_time=0.0, times_for_performance=0.0, context=None):
        return (estimated_time / (times_for_performance or 1.0))

    def _get_quality(self, cr, uid, ids, qty_finished=0.0, qty_scrap=0.0, context=None):
        return ((qty_finished - qty_scrap) / (qty_finished or 1.0))

    def _get_oee(self, cr, uid, ids, wl=False, context=None):
        # OEE = (Availability * Efficiency * Quality) * 100
        wc_obj = self.pool.get('mrp.routing.workcenter')
        uom_obj = self.pool.get('product.uom')
        a = p = q = 0.0
        if wl:
            stop_time = self._get_total_stop_time(cr, uid, ids, wl, context=context)
            times_for_availability = stop_time + wl.time_start + wl.time_stop
            times_for_performance = wl.real_time - stop_time
            qty_finished, qty_real_finished, qty_scrap = self._get_total_qty(cr, uid, ids, wl.production_id, context=context)
            name_routing_workcenter = ((wl.name).split('-')[0])[:-1]
            routing_ids = wc_obj.search(cr, uid,
                                    [('routing_id', '=', wl.routing_id.id),
                                     ('name', 'like', name_routing_workcenter)])
            if routing_ids:
                rout = wc_obj.browse(cr, uid, routing_ids[0])
                factor = qty_finished
                qty_per_cycle = uom_obj._compute_qty(cr, uid,
                                                     rout.uom_id.id,
                                                     rout.qty_per_cycle,
                                                     wl.production_id.bom_id.product_uom.id)
                estimated_time = float((rout.hour_nbr / (qty_per_cycle or 1.0)) * factor)
                time_cycle = rout.hour_nbr
                a = self._get_availability(cr, uid, ids, times_for_availability, estimated_time, time_cycle, qty_per_cycle, factor, context=context)
                p = self._get_performance(cr, uid, ids, estimated_time, times_for_performance, context=context)
                q = self._get_quality(cr, uid, ids, qty_finished, qty_scrap, context=context)
        oee = (a * p * q) * 100
        return (a*100), (p*100), (q*100), oee

    def _get_scrap_and_usage(self, cr, uid, ids, prod=False, context=None):
        qty_finished = real_qty_finished = qty_scrap =0.0
        theo_cost = real_real_cost = 0.0
        scrap = usage = 0.0
        if prod:
            qty_finished = self._calc_finished_qty(cr, uid, ids, prod, context=context)
            real_qty_finished = self._calc_real_finished_qty(cr, uid, ids, prod, context=context)
            qty_scrap = qty_finished - real_qty_finished
            theo_cost = self._get_theo_cost(cr, uid, ids, prod, qty_finished, context=context)
            real_cost = self._get_real_cost(cr, uid, ids, prod, context=context)
            scrap = qty_scrap * (theo_cost / qty_finished)
            for move in prod.move_lines2:
                if move.state != 'done':
                    continue
                scrapped_move = move.location_dest_id.scrap_location
                if scrapped_move:
                    scrap += (move.price_unit * move.product_uom_qty)
            usage = real_cost - theo_cost
            real_real_cost = real_cost + scrap
        return {
           'qty_finished': qty_finished,
           'real_qty_finished': real_qty_finished,
           'qty_scrap': qty_scrap,
           'theo_cost': theo_cost,
           'real_real_cost': real_real_cost,
           'scrap': scrap,
           'usage': usage
        }

    def _get_overweight(self, cr, uid, ids, prod=False, context=None):
        used_weight = theorical_weight = overweight = 0.0
        if prod:
            theorical_weight = prod.product_qty * prod.product_id.weight_net
            qty_finished, qty_real_finished, qty_scrap = self._get_total_qty(cr, uid, ids, prod, context=context)
            theorical_weight = qty_real_finished * prod.product_id.weight_net
            used_weight = 0.0
            for move in prod.move_lines2:
                if move.state != 'done':
                    continue
                scrapped_move = move.location_dest_id.scrap_location
                if not scrapped_move:
                    used_weight += move.product_uom_qty * move.product_id.weight_net
            overweight = 100 * (used_weight - theorical_weight) / (theorical_weight or 1.0)
        return {
           'used_weight': used_weight,
           'theorical_weight': theorical_weight,
           'overweight': overweight
        }

    def _prepare_indicator(self, cr, uid, ids, name_report, company_id, context=None):
        form = self.browse(cr, uid, ids[0])
        return {
            'name': "IND / " + form.name + " / " + time.strftime('%Y-%m-%d %H:%M:%S'),
            'date': time.strftime('%Y-%m-%d'),
            'user_id': uid,
            'company_id': company_id,
            'report_name': form.report_type + " - " + name_report
        }

    def _prepare_indicator_line(self, cr, uid, ids, obj, 
                stop_time, availability, performance, quality, oee, 
                indicator_id, qty_finished, qty_scrap, context=None):
        form = self.browse(cr, uid, ids[0])
        return {
            'name': "INDL / " + form.name + " / " + time.strftime('%Y-%m-%d %H:%M:%S'),
            'date': obj.date_start and (datetime.strptime(obj.date_start, "%Y-%m-%d %H:%M:%S")).strftime('%Y-%m-%d') or False,
            'workcenter_id': obj.workcenter_id and obj.workcenter_id.id or False,
            'qty': qty_finished,
            'product_id': obj.product and obj.product.id or False,
            'stop_time': stop_time,
            'real_time': obj.real_time,
            'tic_time': qty_finished * obj.hour / obj.qty,
            'gasoleo_start':obj.gasoleo_start,
            'gasoleo_stop': obj.gasoleo_stop,
            'availability': availability,
            'performance': performance,
            'quality': quality,
            'oee': oee,
            'indicator_id': indicator_id,
            'qty_scraps': qty_scrap,
            'qty_good': qty_finished - qty_scrap,
            'production_id': obj.production_id and obj.production_id.id or False
        }

    def _prepare_scrap_indicator_line(self, cr, uid, ids, prod,
                qty_finished=0.0, real_qty_finished=0.0, qty_scrap=0.0,
                theo_cost=0.0, real_cost=0.0, usage=0.0, scrap=0.0, indicator_id=False, context=None):
        form = self.browse(cr, uid, ids[0])
        obj = self.pool.get('mrp.production').browse(cr, uid, prod.id)
        return {
            'name': "SCRAPL / " + form.name + " / " + time.strftime('%Y-%m-%d %H:%M:%S'),
            'date': obj.date_start and (datetime.strptime(obj.date_start, "%Y-%m-%d %H:%M:%S")).strftime('%Y-%m-%d') or False,
            'production_id': prod.id,
            'product_id': prod.product_id.id,
            'product_uom': prod.product_uom.id,
            'real_qty': real_qty_finished,
            'theorical_qty': qty_finished,
            'scrap_qty': qty_scrap,
            'real_cost': real_cost,
            'theorical_cost': theo_cost,
            'scrap_cost': scrap,
            'usage_cost': usage,
            'indicator_id': indicator_id
        }

    def _prepare_overweight_indicator_line(self, cr, uid, ids, prod,
                qty_nominal=0.0, qty_consumed=0.0, overweight=0.0, indicator_id=False, context=None):
        form = self.browse(cr, uid, ids[0])
        obj = self.pool.get('mrp.production').browse(cr, uid, prod.id)
        workcenter_id = obj.workcenter_lines.mapped('workcenter_id')
        return {
            'name': "OVERWEIGHTL / " + form.name + " / " + time.strftime('%Y-%m-%d %H:%M:%S'),
            'date': obj.date_start and (datetime.strptime(obj.date_start, "%Y-%m-%d %H:%M:%S")).strftime('%Y-%m-%d') or False,
            'production_id': prod.id,
            'workcenter_id': workcenter_id and workcenter_id[0].id or False,
            'product_id': prod.product_id.id,
            'product_uom': prod.product_uom.id,
            'qty_nominal': qty_nominal,
            'qty_consumed': qty_consumed,
            'overweight': overweight,
            'overweight_abs': abs(overweight),
            'indicator_id': indicator_id
        }

    def _get_productions_by_filters(self, cr, uid, ids, context=None):
        domain = [('state','=','done'), ('production_type','=','normal')]
        form = self.browse(cr, uid, ids[0], context)
        prod_obj = self.pool.get('mrp.production')
        prodwork_line = self.pool.get('mrp.production.workcenter.line')

        if form.date_start and form.date_stop:
            domain.append(('date_start', '>=', form.date_start))
            domain.append(('date_start', '<=', form.date_stop))
            domain.append(('date_finished', '<=', form.date_stop))
            domain.append(('date_finished', '>=', form.date_start))
        if form.routing_id:
            domain.append(('routing_id', '=', form.routing_id.id))
        if form.product_id:
            domain.append(('product_id', '=', form.product_id.id))

        result = prod_obj.search(cr, uid, domain)
        result2 = []

        if form.workcenter_id:
            if result:
                result2 = prodwork_line.search(cr, uid, [('production_id', 'in', result), ('workcenter_id', '=', form.workcenter_id.id)])
                result = []
            else:
                result2 = prodwork_line.search(cr, uid, [('workcenter_id', '=', form.workcenter_id.id)])
            if result2:
                for obj in prodwork_line.browse(cr, uid, result2):
                    result.append(obj.production_id.id)
        return result

    def _calc_finished_qty(self, cr, uid, ids, production, context=None):
        qty = 0.0
        for move in production.move_created_ids2:
            if move.state != 'done':
                continue
            scrapped_move = move.location_dest_id.scrap_location
            if not scrapped_move or (scrapped_move and move.location_id.usage == 'production'):
                qty += move.product_uom_qty
        return qty

    def _calc_real_finished_qty(self, cr, uid, ids, production, context=None):
        qty = 0.0
        for move in production.move_created_ids2:
            if move.state != 'done':
                continue
            scrapped_move = move.location_dest_id.scrap_location
            if not scrapped_move:
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

    def _get_real_cost(self, cr, uid, ids, production, context=None):
        real_cost = 0.0
        for move in production.move_lines2:
            if move.state != 'done':
                continue
            scrapped_move = move.location_dest_id.scrap_location
            if not scrapped_move:
                real_cost += (move.price_unit * move.product_uom_qty)
        return real_cost

    def generate_report_scrap_and_usage(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        indicator_id = False
        prod_obj = self.pool.get('mrp.production')
        ind_obj = self.pool.get('mrp.indicators.scrap')
        ind_line_obj = self.pool.get('mrp.indicators.scrap.line')
        company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id
        company_id = company_id and company_id.id or False
        for form in self.browse(cr, uid, ids, context):
            name_report = self._get_name_by_filters(cr, uid, [form.id], context=context)
            production_ids = self._get_productions_by_filters(cr, uid, ids, context=context)
            vals = self._prepare_indicator(cr, uid, ids, name_report, company_id, context=context)
            indicator_id = ind_obj.create(cr, uid, vals)
            if production_ids and indicator_id:
                for prod in prod_obj.browse(cr, uid, production_ids):
                    result = self._get_scrap_and_usage(cr, uid, ids, prod, context=context)
                    qty_finished = result['qty_finished']
                    real_qty_finished = result['real_qty_finished']
                    qty_scrap = result['qty_scrap']
                    theo_cost = result['theo_cost']
                    real_real_cost = result['real_real_cost']
                    usage = result['usage']
                    scrap = result['scrap']
                    vals = self._prepare_scrap_indicator_line(cr, uid, ids, prod,
                                qty_finished, real_qty_finished, qty_scrap,
                                theo_cost, real_real_cost, usage, scrap,
                                indicator_id, context=context)
                    ind_line_obj.create(cr, uid, vals)
        return indicator_id

    def generate_report_oee(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        wl_obj = self.pool.get('mrp.production.workcenter.line')
        ind_obj = self.pool.get('mrp.indicators.oee')
        ind_line_obj = self.pool.get('mrp.indicators.oee.line')
        ind_avg_obj = self.pool.get('mrp.indicators.oee.summary')
        company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id
        company_id = company_id and company_id.id or False
        indicator_id = False
        for form in self.browse(cr, uid, ids, context):
            name_report = self._get_name_by_filters(cr, uid, [form.id], context=context)
            line_ids = self._get_moves_by_filters(cr, uid, [form.id], context=context)
            vals = self._prepare_indicator(cr, uid, ids, name_report, company_id, context=context)
            indicator_id = ind_obj.create(cr, uid, vals)
            if line_ids and indicator_id:
                for wl in wl_obj.browse(cr, uid, line_ids, context):
                    stop_time = self._get_total_stop_time(cr, uid, ids, wl, context=context)
                    availability, performance, quality, oee = self._get_oee(cr, uid, ids, wl, context=context)
                    qty_finished, qty_real_finished, qty_scrap = self._get_total_qty(cr, uid, ids, wl.production_id, context=context)
                    vals = self._prepare_indicator_line(cr, uid, ids, wl, stop_time, 
                                availability, performance, quality, oee,
                                indicator_id, qty_finished, qty_scrap, context=context)
                    ind_line_obj.create(cr, uid, vals)

                ind = ind_obj.browse(cr, uid, indicator_id)
                tavailability = tperformance = tquality = 0.0
                nline= 0
                vals = {}
                if ind.line_ids:
                    for line in ind.line_ids:
                        workcenter = line.workcenter_id and line.workcenter_id.id or False
                        if workcenter not in vals.keys():
                            vals[workcenter] = {}
                            vals[workcenter]['availability'] = 0.0
                            vals[workcenter]['performance'] = 0.0
                            vals[workcenter]['quality'] = 0.0
                            vals[workcenter]['oee'] = 0.0
                            vals[workcenter]['nline'] = 0
                        vals[workcenter]['availability'] += line.availability
                        vals[workcenter]['performance'] += line.performance
                        vals[workcenter]['quality'] += line.quality
                        vals[workcenter]['nline'] += 1
                        tavailability += line.availability
                        tperformance += line.performance
                        tquality += line.quality
                        nline += 1
                    # Averages per workcenter
                    for key in vals.keys():
                        availability = vals[key]['availability'] / vals[key]['nline']
                        performance = vals[key]['performance'] / vals[key]['nline']
                        quality = vals[key]['quality'] / vals[key]['nline']
                        oee = (availability / 100) * (performance / 100) * (quality / 100) *100
                        ind_avg_obj.create(cr, uid, {
                            'name': _("AVG"),
                            'workcenter_id': key,
                            'availability': availability,
                            'performance': performance,
                            'quality': quality,
                            'oee': oee,
                            'indicator_id': indicator_id
                        })
                    # Averages totals
                    availability = tavailability / nline
                    performance = tperformance / nline
                    quality = tquality / nline
                    oee = (availability / 100) * (performance / 100) * (quality / 100) *100
                    ind_avg_obj.create(cr, uid, {
                        'name': _("TOTAL"),
                        'workcenter_id': False,
                        'availability': availability,
                        'performance': performance,
                        'quality': quality,
                        'oee': oee,
                        'indicator_id': indicator_id
                    })
        return indicator_id

    def generate_report_overweight(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        indicator_id = False
        prod_obj = self.pool.get('mrp.production')
        ind_obj = self.pool.get('mrp.indicators.overweight')
        ind_line_obj = self.pool.get('mrp.indicators.overweight.line')
        ind_avg_obj = self.pool.get('mrp.indicators.overweight.summary')
        company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id
        company_id = company_id and company_id.id or False
        for form in self.browse(cr, uid, ids, context):
            name_report = self._get_name_by_filters(cr, uid, [form.id], context=context)
            production_ids = self._get_productions_by_filters(cr, uid, ids, context=context)
            vals = self._prepare_indicator(cr, uid, ids, name_report, company_id, context=context)
            indicator_id = ind_obj.create(cr, uid, vals)
            if production_ids and indicator_id:
                for prod in prod_obj.browse(cr, uid, production_ids):
                    result = self._get_overweight(cr, uid, ids, prod, context=context)
                    qty_consumed = result['used_weight']
                    qty_nominal = result['theorical_weight']
                    overweight = result['overweight']
                    vals = self._prepare_overweight_indicator_line(cr, uid, ids, prod,
                                qty_nominal, qty_consumed, overweight,
                                indicator_id, context=context)
                    ind_line_obj.create(cr, uid, vals)
                    
                ind = ind_obj.browse(cr, uid, indicator_id)
                tused_weight = ttheorical_weight = 0.0
                vals = {}
                if ind.line_ids:
                    for line in ind.line_ids:
                        workcenter = line.workcenter_id and line.workcenter_id.id or False
                        if workcenter not in vals.keys():
                            vals[workcenter] = {}
                            vals[workcenter]['used_weight'] = 0.0
                            vals[workcenter]['theorical_weight'] = 0.0
                        vals[workcenter]['used_weight'] += line.qty_consumed
                        vals[workcenter]['theorical_weight'] += line.qty_nominal
                        tused_weight += line.qty_consumed
                        ttheorical_weight += line.qty_nominal
                    # Sum per workcenter
                    for key in vals.keys():
                        overweight = 100 * (vals[key]['used_weight'] - vals[key]['theorical_weight']) / (vals[key]['theorical_weight'] or 1.0)
                        ind_avg_obj.create(cr, uid, {
                            'name': _("SUM"),
                            'workcenter_id': key,
                            'qty_consumed': vals[key]['used_weight'],
                            'qty_nominal': vals[key]['theorical_weight'],
                            'overweight': overweight,
                            'overweight_abs': abs(overweight),
                            'indicator_id': indicator_id
                        })
                    # Sum totals
                    overweight = 100 * (tused_weight - ttheorical_weight) / (ttheorical_weight or 1.0)
                    ind_avg_obj.create(cr, uid, {
                        'name': _("TOTAL"),
                        'workcenter_id': False,
                        'qty_consumed': tused_weight,
                        'qty_nominal': ttheorical_weight,
                        'overweight': overweight,
                        'overweight_abs': abs(overweight),
                        'indicator_id': indicator_id
                    })

        return indicator_id

    def generate_performance_calculation(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
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
            elif form.report_type == 'oee':
                new_id = self.generate_report_oee(cr, uid, ids, context)
                value = {
                    'domain': str([('id', 'in', [new_id])]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'mrp.indicators.oee',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'res_id': new_id
                }
            elif form.report_type == 'overweight':
                new_id = self.generate_report_overweight(cr, uid, ids, context)
                value = {
                    'domain': str([('id', 'in', [new_id])]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'mrp.indicators.overweight',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'res_id': new_id
                }
            else:
                value = {}
        return value

performance_calculation()
