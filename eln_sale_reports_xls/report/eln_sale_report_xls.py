# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import xlwt
from openerp.addons.report_xls.report_xls import report_xls
from datetime import datetime
from openerp.report import report_sxw
from openerp.addons.report_xls.utils import _render
from openerp.tools.translate import translate, _


_ir_translation_name = 'eln_sale_report.xls'


class ElnSaleReportXlsParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ElnSaleReportXlsParser, self).__init__(cr, uid, name,
                                                     context=context)

        self.context = context
        self.localcontext.update({'datetime': datetime, '_': _})


class ElnSaleReportXls(report_xls):

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

        self.col_specs_template = {
            'space1': {
                'header': [1, 10, 'text', _render("''")]},
            'space2': {
                'header': [3, 10, 'text', _render("''")]},
            'eu': {
                'header': [5, 10, 'text', _render("_('EUROS')")]},
            'kg': {
                'header': [5, 10, 'text', _render("_('KILES')")]},
            'rent_per': {
                'header': [3, 10, 'text', _render("_(' \%\RENT')")]},
        }

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        report_name = "Ameus Animé"
        ws = wb.add_sheet("1")
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        _ = _p._
        # c_specs = [
        #     ('report_name', 10, 10, 'text', report_name),
        #     ('report_name2', 1, 3, 'text', report_name),
        # ]

        # row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        # row_pos = self.xls_write_row(ws, row_pos, row_data)
        # row_pos += 1
        cell_style = xlwt.easyxf(_xs['xls_title'])

        # Column headers
        c_specs = map(lambda x: self.render(
            x, self.col_specs_template, 'header', render_space={'_': _p._}),
            ['space1', 'space2', 'eu', 'kg'])
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.rh_cell_style,
            set_column_size=True)

        c_specs = map(lambda x: self.render(
            x, self.col_specs_template, 'header', render_space={'_': _p._}),
            ['rent_per'])
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.rh_cell_style,
            set_column_size=True)
        ws.set_horz_split_pos(row_pos)


ElnSaleReportXls('report.eln_sale_report_xls',
                 'eln.sale.report.xls.wzd',
                 parser=ElnSaleReportXlsParser)
