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

from openerp import models, fields, api, _
import time
from datetime import datetime


class PerformanceCalculation(models.TransientModel):
    _name = 'performance.calculation'

    name = fields.Char('Name', size=255, required=True)
    report_type = fields.Selection([
        ('oee', 'OEE'),
        ('scrap_and_usage', 'Scrap & Usage'),
        ('overweight', 'Overweight'),
        ], string='Report type', required=True)
    between_dates = fields.Boolean('Between dates')
    date_start = fields.Date('Date start')
    date_stop = fields.Date('Date stop')
    by_routing = fields.Boolean('By routing')
    routing_id = fields.Many2one('mrp.routing', 'Routing')
    by_product = fields.Boolean('By product')
    product_id = fields.Many2one('product.product', 'Product')
    by_workcenter = fields.Boolean('By workcenter')
    workcenter_id = fields.Many2one('mrp.workcenter', 'Workcenter')

    @api.multi
    def _get_moves_by_filters(self):
        self.ensure_one()
        domain = [
            ('production_state', '=', 'done'),
            ('production_type', '=', 'normal')
        ]
        if self.between_dates and self.date_start and self.date_stop:
            domain.append(('date_start', '>=', self.date_start))
            domain.append(('date_start', '<=', self.date_stop))
            domain.append(('date_finished', '<=', self.date_stop))
            domain.append(('date_finished', '>=', self.date_start))
        if self.by_routing and self.routing_id:
            domain.append(('routing_id', '=', self.routing_id.id))
        if self.by_product and self.product_id:
            domain.append(('product', '=', self.product_id.id))
        if self.by_workcenter and self.workcenter_id:
            domain.append(('workcenter_id', '=', self.workcenter_id.id))
        result = self.env['mrp.production.workcenter.line'].search(domain)
        return result

    @api.multi
    def _get_name_by_filters(self):
        self.ensure_one()
        report_name_comp = ''
        if self.between_dates and self.date_start and self.date_stop:
            report_name_comp += _(" From: ") + self.date_start + _(" to: ") + self.date_stop
        if self.by_routing and self.routing_id:
            report_name_comp += _(" Routing: ") + self.routing_id.name
        if self.by_product and self.product_id:
            report_name_comp += _(" Product: ") + self.product_id.name
        if self.by_workcenter and self.workcenter_id:
            report_name_comp += _(" Workcenter: ") + self.workcenter_id.name
        return report_name_comp

    @api.model
    def _get_total_stop_time(self, wl):
        stop_time = 0.0
        minimum_time = 2.0 / 60.0 # 2 minutos (las iguales o inferiores a este tiempo no se computan)
        production_stops_ids = wl.production_stops_ids.filtered(
            lambda r: r.in_production and r.time > minimum_time)
        for stop in production_stops_ids:
            stop_time += stop.time
        return stop_time

    @api.model
    def _get_total_qty(self, production):
        qty_finished = qty_real_finished = qty_scrap = 0.0
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

    @api.model
    def _get_oee(self, wl=False):
        # OEE = (Availability * Efficiency * Quality) * 100
        wc_obj = self.env['mrp.routing.workcenter']
        uom_obj = self.env['product.uom']
        a = p = q = 0.0
        if wl:
            stop_time = self._get_total_stop_time(wl)
            times_for_availability = stop_time + wl.time_start + wl.time_stop
            times_for_performance = wl.real_time - stop_time
            qty_finished, qty_real_finished, qty_scrap = self._get_total_qty(wl.production_id)
            name_routing_workcenter = ((wl.name).split('-')[0])[:-1]
            domain = [
                ('routing_id', '=', wl.routing_id.id),
                ('name', 'like', name_routing_workcenter)
            ]
            routing_id = wc_obj.search(domain, limit=1)
            if routing_id:
                factor = qty_finished
                qty_per_cycle = uom_obj._compute_qty(
                    routing_id.uom_id.id,
                    routing_id.qty_per_cycle,
                    wl.production_id.bom_id.product_uom.id)
                estimated_time = float((routing_id.hour_nbr / (qty_per_cycle or 1.0)) * factor)
                time_cycle = routing_id.hour_nbr
                a = estimated_time / ((factor * (time_cycle / (qty_per_cycle or 1.0)) + times_for_availability) or 1.0)
                p = estimated_time / (times_for_performance or 1.0)
                q = (qty_finished - qty_scrap) / (qty_finished or 1.0)
        oee = (a * p * q) * 100
        return (a*100), (p*100), (q*100), oee

    @api.model
    def _get_scrap_and_usage(self, prod=False):
        qty_finished = qty_real_finished = qty_scrap = 0.0
        theo_cost = real_real_cost = 0.0
        scrap = usage = 0.0
        if prod:
            qty_finished, qty_real_finished, qty_scrap = self._get_total_qty(prod)
            theo_cost = self._get_theo_cost(prod, qty_finished)
            scrap = qty_scrap * (theo_cost / (qty_finished or 1.0))
            real_cost = 0.0
            for move in prod.move_lines2:
                if move.state != 'done':
                    continue
                scrapped_move = move.location_dest_id.scrap_location
                if scrapped_move:
                    scrap += (move.price_unit * move.product_uom_qty)
                else:
                    real_cost += (move.price_unit * move.product_uom_qty)
            usage = real_cost - theo_cost
            real_real_cost = real_cost + scrap
        return {
           'qty_finished': qty_finished,
           'real_qty_finished': qty_real_finished,
           'qty_scrap': qty_scrap,
           'theo_cost': theo_cost,
           'real_real_cost': real_real_cost,
           'scrap': scrap,
           'usage': usage,
        }

    @api.model
    def _get_overweight(self, prod=False):
        used_weight = theorical_weight = overweight = 0.0
        if prod:
            qty_finished, qty_real_finished, qty_scrap = self._get_total_qty(prod)
            theorical_weight = qty_real_finished * prod.product_id.weight_net
            used_weight = 0.0
            for move in prod.move_lines2:
                if move.state != 'done':
                    continue
                if move.location_dest_id.scrap_location:
                    continue
                if not move.product_id.categ_id.applies_overweight_calculation:
                    continue
                used_weight += move.product_uom_qty * move.product_id.weight_net
            overweight = 100 * (used_weight - theorical_weight) / (theorical_weight or 1.0)
        return {
           'used_weight': used_weight,
           'theorical_weight': theorical_weight,
           'overweight': overweight,
        }

    @api.model
    def _get_theorical_overweight(self, prod=False):
        theorical_overweight = 0.0
        if prod and prod.bom_id:
            qty = qty_final = 0.0
            for line in prod.bom_id.bom_line_ids:
                if not line.product_id.categ_id.applies_overweight_calculation:
                    continue
                qty += line.product_qty
                qty_final += line.product_qty * (line.product_efficiency or 1.0)
            theorical_overweight = (100 - (100 * qty_final / qty)) if qty else 0.0
        return round(theorical_overweight, 2)

    @api.multi
    def _prepare_indicator(self, name_report, company_id):
        self.ensure_one()
        res = {
            'name': "IND / " + self.name + " / " + time.strftime('%Y-%m-%d %H:%M:%S'),
            'date': time.strftime('%Y-%m-%d'),
            'user_id': self._uid,
            'company_id': company_id,
            'report_name': self.report_type + " - " + name_report,
        }
        return res

    @api.multi
    def _prepare_indicator_line(self, indicator_id, wl, stop_time, qty_finished, qty_scrap,
            availability, performance, quality, oee):
        self.ensure_one()
        res = {
            'name': "INDL / " + self.name + " / " + time.strftime('%Y-%m-%d %H:%M:%S'),
            'date': wl.date_start and (datetime.strptime(wl.date_start, "%Y-%m-%d %H:%M:%S")).strftime('%Y-%m-%d') or False,
            'production_id': wl.production_id and wl.production_id.id or False,
            'workcenter_id': wl.workcenter_id and wl.workcenter_id.id or False,
            'product_id': wl.product and wl.product.id or False,
            'qty': qty_finished,
            'stop_time': stop_time,
            'real_time': wl.real_time,
            'tic_time': qty_finished * wl.hour * (wl.availability_ratio or 1.0) / wl.qty, # Multiplicamos por availability_ratio porque obj.hour está influenciado por ese ratio y no queremos que influya en este cálculo
            'gasoleo_start': wl.gasoleo_start,
            'gasoleo_stop': wl.gasoleo_stop,
            'availability': availability,
            'performance': performance,
            'quality': quality,
            'oee': oee,
            'qty_scraps': qty_scrap,
            'qty_good': qty_finished - qty_scrap,
            'indicator_id': indicator_id,
        }
        return res

    @api.multi
    def _prepare_scrap_indicator_line(self, indicator_id, prod, qty_finished=0.0, real_qty_finished=0.0,
            qty_scrap=0.0, theo_cost=0.0, real_cost=0.0, usage=0.0, scrap=0.0):
        self.ensure_one()
        res = {
            'name': "SCRAPL / " + self.name + " / " + time.strftime('%Y-%m-%d %H:%M:%S'),
            'date': prod.date_start and (datetime.strptime(prod.date_start, "%Y-%m-%d %H:%M:%S")).strftime('%Y-%m-%d') or False,
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
            'indicator_id': indicator_id,
        }
        return res

    @api.multi
    def _prepare_overweight_indicator_line(self, indicator_id, prod, qty_nominal=0.0,
            qty_consumed=0.0, overweight=0.0):
        self.ensure_one()
        workcenter_id = prod.workcenter_lines.mapped('workcenter_id')
        res = {
            'name': "OVERWEIGHTL / " + self.name + " / " + time.strftime('%Y-%m-%d %H:%M:%S'),
            'date': prod.date_start and (datetime.strptime(prod.date_start, "%Y-%m-%d %H:%M:%S")).strftime('%Y-%m-%d') or False,
            'production_id': prod.id,
            'workcenter_id': workcenter_id and workcenter_id[0].id or False,
            'product_id': prod.product_id.id,
            'product_uom': prod.product_uom.id,
            'qty_nominal': qty_nominal,
            'qty_consumed': qty_consumed,
            'overweight': overweight,
            'overweight_abs': abs(overweight),
            'indicator_id': indicator_id,
        }
        return res

    @api.multi
    def _get_productions_by_filters(self):
        self.ensure_one()
        domain = [
            ('state', '=', 'done'),
            ('production_type', '=', 'normal')
        ]
        prod_obj = self.env['mrp.production']
        prodwork_line = self.env['mrp.production.workcenter.line']
        if self.between_dates and self.date_start and self.date_stop:
            domain.append(('date_start', '>=', self.date_start))
            domain.append(('date_start', '<=', self.date_stop))
            domain.append(('date_finished', '<=', self.date_stop))
            domain.append(('date_finished', '>=', self.date_start))
        if self.by_routing and self.routing_id:
            domain.append(('routing_id', '=', self.routing_id.id))
        if self.by_product and self.product_id:
            domain.append(('product_id', '=', self.product_id.id))
        res = prod_obj.search(domain)
        if self.by_workcenter and self.workcenter_id and res:
            res2 = prodwork_line.search([
                ('production_id', 'in', res._ids),
                ('workcenter_id', '=', self.workcenter_id.id)
            ])
            res = res2.mapped('production_id')
        return res

    @api.model
    def _get_theo_cost(self, production, product_uom_qty=0.0):
        theorical_cost = 0.0
        if production.theo_cost:
            theorical_cost = production.theo_cost * product_uom_qty
        else:
            tmpl_obj = self.env['product.template']
            updated_price = tmpl_obj._calc_price(production.bom_id, test=True)
            theorical_cost = updated_price * product_uom_qty
        return theorical_cost

    @api.multi
    def generate_report_scrap_and_usage(self):
        self.ensure_one()
        ind_obj = self.env['mrp.indicators.scrap']
        ind_line_obj = self.env['mrp.indicators.scrap.line']
        company_id = self.env.user.company_id.id
        name_report = self._get_name_by_filters()
        production_ids = self._get_productions_by_filters()
        vals = self._prepare_indicator(name_report, company_id)
        indicator_id = ind_obj.create(vals)
        if production_ids and indicator_id:
            for prod in production_ids:
                result = self._get_scrap_and_usage(prod)
                qty_finished = result['qty_finished']
                real_qty_finished = result['real_qty_finished']
                qty_scrap = result['qty_scrap']
                theo_cost = result['theo_cost']
                real_real_cost = result['real_real_cost']
                usage = result['usage']
                scrap = result['scrap']
                vals = self._prepare_scrap_indicator_line(
                    indicator_id.id, prod, qty_finished, real_qty_finished,
                    qty_scrap, theo_cost, real_real_cost, usage, scrap)
                ind_line_obj.create(vals)
        return indicator_id.id

    @api.multi
    def generate_report_oee(self):
        self.ensure_one()
        ind_obj = self.env['mrp.indicators.oee']
        ind_line_obj = self.env['mrp.indicators.oee.line']
        ind_avg_obj = self.env['mrp.indicators.oee.summary']
        company_id = self.env.user.company_id.id
        name_report = self._get_name_by_filters()
        line_ids = self._get_moves_by_filters()
        vals = self._prepare_indicator(name_report, company_id)
        indicator_id = ind_obj.create(vals)
        if line_ids and indicator_id:
            for wl in line_ids:
                stop_time = self._get_total_stop_time(wl)
                qty_finished, qty_real_finished, qty_scrap = self._get_total_qty(wl.production_id)
                availability, performance, quality, oee = self._get_oee(wl)
                vals = self._prepare_indicator_line(
                    indicator_id.id, wl, stop_time, qty_finished, qty_scrap,
                    availability, performance, quality, oee)
                ind_line_obj.create(vals)
            tavailability = tperformance = tquality = 0.0
            nline= 0
            if indicator_id.line_ids:
                vals = {}
                for line in indicator_id.line_ids:
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
                # Averages by workcenter
                for key in vals.keys():
                    availability = vals[key]['availability'] / vals[key]['nline']
                    performance = vals[key]['performance'] / vals[key]['nline']
                    quality = vals[key]['quality'] / vals[key]['nline']
                    oee = (availability / 100) * (performance / 100) * (quality / 100) * 100
                    ind_avg_obj.create({
                        'name': _("AVG"),
                        'workcenter_id': key,
                        'product_id': False,
                        'availability': availability,
                        'performance': performance,
                        'quality': quality,
                        'oee': oee,
                        'summary_type': 'workcenter',
                        'indicator_id': indicator_id.id,
                    })
                vals = {}
                for line in indicator_id.line_ids:
                    product = line.product_id and line.product_id.id or False
                    if product not in vals.keys():
                        vals[product] = {}
                        vals[product]['availability'] = 0.0
                        vals[product]['performance'] = 0.0
                        vals[product]['quality'] = 0.0
                        vals[product]['oee'] = 0.0
                        vals[product]['nline'] = 0
                    vals[product]['availability'] += line.availability
                    vals[product]['performance'] += line.performance
                    vals[product]['quality'] += line.quality
                    vals[product]['nline'] += 1
                # Averages by product
                for key in vals.keys():
                    availability = vals[key]['availability'] / vals[key]['nline']
                    performance = vals[key]['performance'] / vals[key]['nline']
                    quality = vals[key]['quality'] / vals[key]['nline']
                    oee = (availability / 100) * (performance / 100) * (quality / 100) * 100
                    ind_avg_obj.create({
                        'name': _("AVG"),
                        'workcenter_id': False,
                        'product_id': key,
                        'availability': availability,
                        'performance': performance,
                        'quality': quality,
                        'oee': oee,
                        'summary_type': 'product',
                        'indicator_id': indicator_id.id,
                    })
                # Averages totals
                availability = tavailability / nline
                performance = tperformance / nline
                quality = tquality / nline
                oee = (availability / 100) * (performance / 100) * (quality / 100) * 100
                ind_avg_obj.create({
                    'name': _("TOTAL"),
                    'workcenter_id': False,
                    'product_id': False,
                    'availability': availability,
                    'performance': performance,
                    'quality': quality,
                    'oee': oee,
                    'summary_type': 'total',
                    'indicator_id': indicator_id.id,
                })
        return indicator_id.id

    @api.multi
    def generate_report_overweight(self):
        self.ensure_one()
        ind_obj = self.env['mrp.indicators.overweight']
        ind_line_obj = self.env['mrp.indicators.overweight.line']
        ind_avg_obj = self.env['mrp.indicators.overweight.summary']
        company_id = self.env.user.company_id.id
        name_report = self._get_name_by_filters()
        production_ids = self._get_productions_by_filters()
        vals = self._prepare_indicator(name_report, company_id)
        indicator_id = ind_obj.create(vals)
        if production_ids and indicator_id:
            for prod in production_ids:
                result = self._get_overweight(prod)
                qty_consumed = result['used_weight']
                qty_nominal = result['theorical_weight']
                overweight = result['overweight']
                vals = self._prepare_overweight_indicator_line(
                    indicator_id.id, prod, qty_nominal, qty_consumed, overweight)
                ind_line_obj.create(vals)
            tused_weight = ttheorical_weight = 0.0
            vals = {}
            if indicator_id.line_ids:
                for line in indicator_id.line_ids:
                    workcenter = line.workcenter_id and line.workcenter_id.id or False
                    if workcenter not in vals.keys():
                        vals[workcenter] = {}
                        vals[workcenter]['used_weight'] = 0.0
                        vals[workcenter]['theorical_weight'] = 0.0
                    vals[workcenter]['used_weight'] += line.qty_consumed
                    vals[workcenter]['theorical_weight'] += line.qty_nominal
                    tused_weight += line.qty_consumed
                    ttheorical_weight += line.qty_nominal
                # Sum by workcenter
                for key in vals.keys():
                    overweight = 100 * (vals[key]['used_weight'] - vals[key]['theorical_weight']) / (vals[key]['theorical_weight'] or 1.0)
                    ind_avg_obj.create({
                        'name': _("SUM"),
                        'workcenter_id': key,
                        'qty_consumed': vals[key]['used_weight'],
                        'qty_nominal': vals[key]['theorical_weight'],
                        'overweight': overweight,
                        'overweight_abs': abs(overweight),
                        'indicator_id': indicator_id.id,
                    })
                # Sum totals
                overweight = 100 * (tused_weight - ttheorical_weight) / (ttheorical_weight or 1.0)
                ind_avg_obj.create({
                    'name': _("TOTAL"),
                    'workcenter_id': False,
                    'qty_consumed': tused_weight,
                    'qty_nominal': ttheorical_weight,
                    'overweight': overweight,
                    'overweight_abs': abs(overweight),
                    'indicator_id': indicator_id.id,
                })
        return indicator_id.id

    @api.multi
    def generate_performance_calculation(self):
        for wzd in self:
            if wzd.report_type == 'scrap_and_usage':
                new_id = wzd.generate_report_scrap_and_usage()
                res = {
                    'domain': str([('id', 'in', [new_id])]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'mrp.indicators.scrap',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'res_id': new_id,
                }
            elif wzd.report_type == 'oee':
                new_id = wzd.generate_report_oee()
                res = {
                    'domain': str([('id', 'in', [new_id])]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'mrp.indicators.oee',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'res_id': new_id,
                }
            elif wzd.report_type == 'overweight':
                new_id = wzd.generate_report_overweight()
                res = {
                    'domain': str([('id', 'in', [new_id])]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'mrp.indicators.overweight',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'res_id': new_id,
                }
            else:
                res = {}
        return res
