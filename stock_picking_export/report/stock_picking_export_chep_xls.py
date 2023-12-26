# -*- coding: utf-8 -*-
# Copyright 2023 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import xlwt
from openerp.addons.report_xls.report_xls import report_xls
from datetime import datetime
from openerp.report import report_sxw
from openerp.addons.report_xls.utils import rowcol_to_cell


class StockPickingExportChepXlsParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(StockPickingExportChepXlsParser, self).\
            __init__(cr, uid, name, context=context)
        self.context = context
        self.localcontext.update({
            'datetime': datetime,
        })


class StockPickingExportChepXls(report_xls):
    column_sizes = [12, 16, 24, 20, 12, 18, 16, 12]

    def __init__(self, name, table, rml=False, parser=False,
                 header=True, store=False):
        super(StockPickingExportChepXls, self).\
            __init__(name, table, rml, parser, header, store)

        _xs = self.xls_styles
        rh_cell_format = _xs['bold'] + _xs['borders_all']
        # lines
        aml_cell_format = ''
        self.aml_cell_style = xlwt.easyxf(aml_cell_format)
        self.aml_cell_style_center = xlwt.easyxf(aml_cell_format +
                                                 _xs['center'])
        self.aml_cell_style_date = \
            xlwt.easyxf(aml_cell_format + _xs['left'],
                        num_format_str='DD-MM-YYYY')
        self.aml_cell_style_decimal2 = \
            xlwt.easyxf(aml_cell_format + _xs['right'],
                        num_format_str='#,##0.00')
        self.aml_cell_style_decimal3 = \
            xlwt.easyxf(aml_cell_format + _xs['right'],
                        num_format_str='#,##0.000')
        self.rh_cell_style = xlwt.easyxf(rh_cell_format)
        self.borders_all_black = ('borders: '
            'left thin, right thin, top thin, bottom thin, '
            'left_colour black, right_colour black, '
            'top_colour black, bottom_colour black;')


    def global_initializations(self, wb, _p, xlwt, _xs, objects, data):
        # this procedure will initialise variables and Excel cell styles and
        # return them as global ones
        self.ws = wb.add_sheet('Plantilla de Transferencias')
        self.nbr_columns = 8
        # Title style
        self.style_font12 = xlwt.easyxf(_xs['xls_title'] + _xs['center'])
        # Header Style
        self.style_grey_center = xlwt.easyxf(
            _xs['fill_grey'] + self.borders_all_black + _xs['center'])
        self.style_blue_left = xlwt.easyxf(
            _xs['fill_blue'] + self.borders_all_black + _xs['left'])

    def print_empty_row(self, row_pos):
        c_sizes = self.column_sizes
        c_specs = [('empty%s' % i, 1, c_sizes[i], 'text', None)
                   for i in range(0, len(c_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            self.ws, row_pos, row_data, set_column_size=True)
        return row_pos

    def print_header_titles(self, row_pos):
        style1 = self.style_blue_left
        c_specs = [
            ('a', 1, 0, 'text', u'UBICACIÓN', None, style1),
            ('b', 1, 0, 'text', 'CONTRAPARTIDA', None, style1),
            ('c', 1, 0, 'text', 'TIPO DE TRANSFERENCIA', None, style1),
            ('d', 1, 0, 'text', 'FECHA DE ENTREGA', None, style1),
            ('e', 1, 0, 'text', 'REF', None, style1),
            ('f', 1, 0, 'text', 'OTRA REFERENCIA', None, style1),
            ('g', 1, 0, 'text', 'TIPO DE PALLET', None, style1),
            ('h', 1, 0, 'text', 'CANTIDAD', None, style1),
]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(self.ws, row_pos, row_data)
        return row_pos

    def _print_report_values(self, data, row_pos):
        for line in data['lines']:
            col0 = line['company_code']
            col1 = line['partner_code']
            col2 = line['transfer_type']
            col3 = line['picking_date']
            col4 = line['picking_name']
            col5 = line['other_ref']
            col6 = line['supplier_product_code']
            col7 = line['qty']
            c_specs = [
                ('a', 1, 0, 'text', col0, None, None),
                ('b', 1, 0, 'text', col1, None, None),
                ('c', 1, 0, 'text', col2, None, None),
                ('d', 1, 0, 'text', col3, None, None),
                ('e', 1, 0, 'text', col4, None, None),
                ('f', 1, 0, 'text', col5, None, None),
                ('g', 1, 0, 'text', col6, None, None),
                ('h', 1, 0, 'number', col7, None, None),
            ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(self.ws, row_pos, row_data)
        return row_pos

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        # Initializations
        self.global_initializations(wb, _p, xlwt, _xs, objects, data)
        row_pos = 0
        # Headers
        row_pos = self.print_header_titles(row_pos)
        # Values
        row_pos = self._print_report_values(data, row_pos)
        # Print empty row to define column sizes
        row_pos = self.print_empty_row(row_pos)


StockPickingExportChepXls('report.stock_picking_export_chep_xls',
                      'stock.picking.export',
                      parser=StockPickingExportChepXlsParser)
