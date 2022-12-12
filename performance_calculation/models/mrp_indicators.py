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

from openerp import api, models, fields
import openerp.addons.decimal_precision as dp


class MrpIndicatorsOee(models.Model):
    _name = 'mrp.indicators.oee'
    _order = 'date desc, id desc'

    name = fields.Char('Name', size=255, required=True)
    line_ids = fields.One2many(
        'mrp.indicators.oee.line', 'indicator_id', 'Lines')
    line_summary_by_workcenter_ids = fields.One2many(
        'mrp.indicators.oee.summary', 'indicator_id', 'Summary by workcenter',
        domain=[('summary_type', 'in', ('workcenter', 'total'))])
    line_summary_by_product_ids = fields.One2many(
        'mrp.indicators.oee.summary', 'indicator_id', 'Summary by product',
        domain=[('summary_type', 'in', ('product', 'total'))])
    date = fields.Date('Date')
    user_id = fields.Many2one('res.users', 'User')
    company_id = fields.Many2one('res.company', 'Company')
    report_name = fields.Char('Report', size=255)


class MrpIndicatorsOeeLine(models.Model):
    _name = 'mrp.indicators.oee.line'

    name = fields.Char('Name', size=255, required=True)
    date = fields.Date('Date')
    workcenter_id = fields.Many2one('mrp.workcenter', 'Workcenter')
    production_id = fields.Many2one('mrp.production', 'Production')
    qty = fields.Float('Qty',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        required=True)
    qty_scraps = fields.Float('Scraps',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    qty_good = fields.Float('Real qty',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    product_id = fields.Many2one('product.product', 'Product',
        required=True)
    stop_time = fields.Float('Stop time')
    real_time = fields.Float('Real time')
    tic_time = fields.Float('TiC time')
    time_start = fields.Float('Time start')
    time_stop = fields.Float('Time stop')
    gasoleo_start = fields.Float('Gasoleo start')
    gasoleo_stop = fields.Float('Gasoleo stop')
    oee = fields.Float('OEE')
    availability = fields.Float('Availability')
    performance = fields.Float('Performance')
    quality = fields.Float('Quality')
    indicator_id = fields.Many2one('mrp.indicators.oee', 'Indicator',
        ondelete='cascade', required=True)


class MrpIndicatorsOeeSummary(models.Model):
    _name = 'mrp.indicators.oee.summary'
    _order = 'workcenter_id, product_id'

    name = fields.Char('Name', size=255, required=True)
    workcenter_id = fields.Many2one('mrp.workcenter', 'Workcenter')
    product_id = fields.Many2one('product.product', 'Product')
    oee = fields.Float('OEE')
    availability = fields.Float('Availability')
    performance = fields.Float('Performance')
    quality = fields.Float('Quality')
    summary_type = fields.Selection([
        ('workcenter', 'Workcenter'),
        ('product', 'Product'),
        ('total', 'Total'),
        ], string='Summary type', required=True,
        default='total')
    indicator_id = fields.Many2one('mrp.indicators.oee', 'Indicator',
        ondelete='cascade', required=True)


class MrpIndicatorsScrap(models.Model):
    _name = 'mrp.indicators.scrap'
    _order = 'date desc, id desc'

    name = fields.Char('Name', size=255, required=True)
    line_ids = fields.One2many(
        'mrp.indicators.scrap.line', 'indicator_id', 'Lines')
    date = fields.Date('Date')
    user_id = fields.Many2one('res.users', 'User')
    company_id = fields.Many2one('res.company', 'Company')
    report_name = fields.Char('Report', size=255)


class MrpIndicatorsScrapLine(models.Model):
    _name = 'mrp.indicators.scrap.line'

    name = fields.Char('Name', size=255, required=True)
    date = fields.Date('Date')
    production_id = fields.Many2one('mrp.production', 'Production')
    product_id = fields.Many2one('product.product', 'Product')
    product_uom = fields.Many2one('product.uom', 'Unit of Measure')
    real_qty = fields.Float('Real qty',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    theorical_qty = fields.Float('Total qty.',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    scrap_qty = fields.Float('Scrap qty.',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    real_cost = fields.Float('Real cost',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    theorical_cost = fields.Float('Theorical cost',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    scrap_cost = fields.Float('Scrap',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    usage_cost = fields.Float('Usage',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    inventory_cost = fields.Float('Inventory cost',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    indicator_id = fields.Many2one('mrp.indicators.scrap', 'Indicator',
        ondelete='cascade', required=True)


class MrpIndicatorsOverweight(models.Model):
    _name = 'mrp.indicators.overweight'
    _order = 'date desc, id desc'

    name = fields.Char('Name', size=255, required=True)
    line_ids = fields.One2many(
        'mrp.indicators.overweight.line', 'indicator_id', 'Lines')
    line_summary_ids = fields.One2many(
        'mrp.indicators.overweight.summary', 'indicator_id', 'Summary')
    date = fields.Date('Date')
    user_id = fields.Many2one('res.users', 'User')
    company_id = fields.Many2one('res.company', 'Company')
    report_name = fields.Char('Report', size=255)


class MrpIndicatorsOverweightLine(models.Model):
    _name = 'mrp.indicators.overweight.line'

    name = fields.Char('Name', size=255, required=True)
    date = fields.Date('Date')
    production_id = fields.Many2one('mrp.production', 'Production')
    workcenter_id = fields.Many2one('mrp.workcenter', 'Workcenter')
    product_id = fields.Many2one('product.product', 'Product')
    product_uom = fields.Many2one('product.uom', 'Unit of Measure')
    qty_nominal = fields.Float('Qty nominal',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    qty_consumed = fields.Float('Qty consumed',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    overweight = fields.Float('Overweight (%)')
    overweight_abs = fields.Float('Overweight Abs')
    indicator_id = fields.Many2one('mrp.indicators.overweight', 'Indicator',
        ondelete='cascade', required=True)


class MrpIndicatorsOverweightSummary(models.Model):
    _name = 'mrp.indicators.overweight.summary'

    name = fields.Char('Name', size=255, required=True)
    workcenter_id = fields.Many2one('mrp.workcenter', 'Workcenter')
    qty_nominal = fields.Float('Qty nominal',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    qty_consumed = fields.Float('Qty consumed',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    overweight = fields.Float('Overweight (%)')
    overweight_abs = fields.Float('Overweight Abs')
    indicator_id = fields.Many2one('mrp.indicators.overweight', 'Indicator',
        ondelete='cascade', required=True)
