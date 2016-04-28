# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import xlwt
from openerp.addons.report_xls.report_xls import report_xls
from datetime import datetime
from openerp.report import report_sxw
# from openerp.addons.report_xls.utils import _render
from openerp.tools.translate import _


_ir_translation_name = 'eln_sale_report.xls'


class ElnSaleReportXlsParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ElnSaleReportXlsParser, self).__init__(cr, uid, name,
                                                     context=context)

        self.context = context
        self.localcontext.update({'datetime': datetime, '_': _})


class ElnSaleReportXls(report_xls):
    column_sizes = [30, 20, 10, 10, 20, 15, 15, 15, 15, 20, 15, 15, 15, 15]

    def __init__(self, name, table, rml=False, parser=False,
                 header=True, store=False):
        super(ElnSaleReportXls, self).\
            __init__(name, table, rml, parser, header, store)

        _xs = self.xls_styles
        rh_cell_format = _xs['bold'] + _xs['borders_all']
        # lines
        aml_cell_format = _xs['borders_all']
        self.aml_cell_style = xlwt.easyxf(aml_cell_format)
        self.aml_cell_style_center = xlwt.easyxf(aml_cell_format +
                                                 _xs['center'])
        self.aml_cell_style_date = \
            xlwt.easyxf(aml_cell_format + _xs['left'],
                        num_format_str=report_xls.date_format)
        self.aml_cell_style_decimal = \
            xlwt.easyxf(aml_cell_format + _xs['right'],
                        num_format_str=report_xls.decimal_format)
        self.rh_cell_style = xlwt.easyxf(rh_cell_format)

    def global_initializations(self, wb, _p, xlwt, _xs, objects, data):
        # this procedure will initialise variables and Excel cell styles and
        # return them as global ones
        self.ws = wb.add_sheet(_("Dayly sale report"))
        self.nbr_columns = 14
        # Tytle style
        self.style_font12 = xlwt.easyxf(_xs['xls_title'] + _xs['center'])
        # Header Style
        self.style_bold_blue_center = xlwt.easyxf(
            _xs['bold'] + _xs['fill_blue'] + _xs['borders_all'] +
            _xs['center'])

    def print_title(self, row_pos):
        report_name = ' - '.join(["DAYLY SALE REPORT", 'MES', 'AÑO'],)
        c_specs = [('report_name', self.nbr_columns, 0, 'text', report_name)]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            self.ws, row_pos, row_data, row_style=self.style_font12)
        return row_pos

    # send an empty row to the Excel document
    def print_empty_row(self, row_pos):
        c_sizes = self.column_sizes
        c_specs = [('empty%s' % i, 1, c_sizes[i], 'text', None)
                   for i in range(0, len(c_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            self.ws, row_pos, row_data, set_column_size=True)
        return row_pos

    def print_header_titles(self, data, row_pos):
        style1 = self.style_bold_blue_center
        # PART 1
        c_specs = [
            ('a', 1, 0, 'text', None, None, None),
            ('b', 3, 0, 'text', None, None, None),
            ('c', 5, 0, 'text', _('EUROS'), None, style1),
            ('d', 5, 0, 'text', _('KILES'), None, style1),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(self.ws, row_pos, row_data)
        # PART 2
        c_specs = [
            ('a', 1, 0, 'text', None, None, None),
            ('b', 3, 0, 'text', _('% RENT'), None, style1),
            ('c', 2, 0, 'text', _('ACUMULED'), None, style1),
            ('d', 1, 0, 'text', _('OF DAY'), None, style1),
            ('e', 1, 0, 'text', _('PREVIOUS DAY'), None, style1),
            ('f', 1, 0, 'text', _('QUOTATION'), None, style1),
            ('g', 2, 0, 'text', _('ACUMULED'), None, style1),
            ('h', 1, 0, 'text', _('OF DAY'), None, style1),
            ('i', 1, 0, 'text', _('PREVIOUS DAY'), None, style1),
            ('j', 1, 0, 'text', _('QUOTATION'), None, style1),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(self.ws, row_pos, row_data)
        # PART 2
        c_specs = [
            ('a', 1, 0, 'text', None, None, None),
            ('b', 1, 0, 'text', _('CURRENT'), None, style1),
            ('c', 1, 0, 'text', _('PREV.'), None, style1),
            ('d', 1, 0, 'text', _('NEXT.'), None, style1),
            ('e', 1, 0, 'text', _('CURRENTS'), None, style1),
            ('f', 1, 0, 'text', _('PREVIOUS'), None, style1),
            ('g', 1, 0, 'text', None, None, style1),
            ('h', 1, 0, 'text', None, None, style1),
            ('i', 1, 0, 'text', None, None, style1),
            ('j', 1, 0, 'text', _('CURRENTS'), None, style1),
            ('k', 1, 0, 'text', _('PREVIOUS'), None, style1),
            ('l', 1, 0, 'text', None, None, style1),
            ('m', 1, 0, 'text', None, None, style1),
            ('n', 1, 0, 'text', None, None, style1),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(self.ws, row_pos, row_data)
        return row_pos

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        # report_name = "Ameus Animé"
        # ws = wb.add_sheet("1")
        # ws.panes_frozen = True
        # ws.remove_splits = True
        # ws.portrait = 0  # Landscape
        # ws.fit_width_to_pages = 1
        # row_pos = 0
        # ws.header_str = self.xls_headers['standard']
        # ws.footer_str = self.xls_footers['standard']

        # Initializations
        self.global_initializations(wb, _p, xlwt, _xs, objects, data)
        row_pos = 0
        # Report Title
        row_pos = self.print_title(row_pos)
        # Print empty row to define column sizes
        row_pos = self.print_empty_row(row_pos)

        # Headers
        row_pos = self.print_header_titles(self, row_pos)
        # _ = _p._
        # # c_specs = [
        # #     ('report_name', 10, 10, 'text', report_name),
        # #     ('report_name2', 1, 3, 'text', report_name),
        # # ]

        # # row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        # # row_pos = self.xls_write_row(ws, row_pos, row_data)
        # # row_pos += 1
        # cell_style = xlwt.easyxf(_xs['xls_title'])

        # # Column headers
        # c_specs = map(lambda x: self.render(
        #     x, self.col_specs_template, 'header', render_space={'_': _p._}),
        #     ['space1', 'space2', 'eu', 'kg'])
        # row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        # row_pos = self.xls_write_row(
        #     ws, row_pos, row_data, row_style=self.rh_cell_style,
        #     set_column_size=True)

        # c_specs = map(lambda x: self.render(
        #     x, self.col_specs_template, 'header', render_space={'_': _p._}),
        #     ['rent_per'])
        # row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        # row_pos = self.xls_write_row(
        #     ws, row_pos, row_data, row_style=self.rh_cell_style,
        #     set_column_size=True)
        # # ws.set_horz_split_pos(row_pos)


ElnSaleReportXls('report.eln_sale_report_xls',
                 'eln.sale.report.xls.wzd',
                 parser=ElnSaleReportXlsParser)
