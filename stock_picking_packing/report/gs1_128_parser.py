# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, _
from openerp.exceptions import except_orm


class Gs1_128ParserX1(models.AbstractModel):
    _name = 'report.stock_picking_packing.gs1_128_report_x1'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report_name = 'stock_picking_packing.gs1_128_report_x1'
        if not data:
            raise except_orm(_('Error'),
                             _('You must print it from a wizard'))
        line_objs = {}
        for picking_id in data['lines_dic']:
            picking = self.env['stock.picking'].browse(int(picking_id))
            line_objs[picking] = data['lines_dic'][picking_id]

        docargs = {
            'doc_ids': [],
            'doc_model': 'stock.picking',
            'docs': line_objs.keys(),
            'line_objs': line_objs
        }
        return report_obj.render(report_name, docargs)


class Gs1_128ParserX2(models.AbstractModel):
    _name = 'report.stock_picking_packing.gs1_128_report_x2'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report_name = 'stock_picking_packing.gs1_128_report_x2'
        if not data:
            raise except_orm(_('Error'),
                             _('You must print it from a wizard'))
        line_objs = {}
        for picking_id in data['lines_dic']:
            picking = self.env['stock.picking'].browse(int(picking_id))
            line_objs[picking] = data['lines_dic'][picking_id]

        docargs = {
            'doc_ids': [],
            'doc_model': 'stock.picking',
            'docs': line_objs.keys(),
            'line_objs': line_objs
        }
        return report_obj.render(report_name, docargs)
