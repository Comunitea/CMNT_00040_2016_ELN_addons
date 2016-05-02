# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import xlwt
from openerp.addons.report_xls.report_xls import report_xls
from datetime import datetime
from openerp.report import report_sxw
# from openerp.addons.report_xls.utils import _render
from openerp.tools.translate import _


_ir_translation_name = 'eln_salesman_summary.xls'


class ElnSalesmanSummaryXlsParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ElnSalesmanSummaryXlsParser, self).__init__(cr, uid, name,
                                                          context=context)

        self.context = context
        self.localcontext.update({'datetime': datetime, '_': _})


class ElnSalesmanSummaryXls(report_xls):
    column_sizes = [30, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15]

    def __init__(self, name, table, rml=False, parser=False,
                 header=True, store=False):
        super(ElnSalesmanSummaryXls, self).\
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
        self.ws = wb.add_sheet(_("Salesman Sale Summary"))
        self.nbr_columns = 14
        # Tytle style
        self.style_font12 = xlwt.easyxf(_xs['xls_title'] + _xs['center'])
        # Header Style
        self.style_bold_blue_center = xlwt.easyxf(
            _xs['bold'] + _xs['fill_blue'] + _xs['borders_all'] +
            _xs['center'])

    def print_title(self, objects, row_pos):
        report_name = '-'.join([_("SALESMAN SALE SUMMARY"), objects.start_date,
                               objects.end_date])
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

    def print_header_titles(self, row_pos):
        style1 = self.style_bold_blue_center
        # PART 1
        c_specs = [
            ('a', 1, 0, 'text', None, None, None),
            ('bcde', 4, 0, 'text', _('COMERCIAL VALQUIN'), None, style1),
            ('bcde', 4, 0, 'text', _('COMERCIAL VALQUIN INDIRECT'), None,
             style1),
            ('fghi', 4, 0, 'text', _('QUIVAL S.A'), None, style1),
            ('jklm', 4, 0, 'text', _('TOTAL'), None, style1),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(self.ws, row_pos, row_data)
        # PART 2
        c_specs = [
            ('a', 1, 0, 'text', _('SALESMAN'), None, style1),
            ('b', 1, 0, 'text', _('SALES'), None, style1),
            ('c', 1, 0, 'text', _('COST'), None, style1),
            ('d', 1, 0, 'text', _('BENEFIT'), None, style1),
            ('e', 1, 0, 'text', _('BENEFIT %'), None, style1),
            ('f', 1, 0, 'text', _('SALES'), None, style1),
            ('g', 1, 0, 'text', _('COST'), None, style1),
            ('h', 1, 0, 'text', _('BENEFIT'), None, style1),
            ('i', 1, 0, 'text', _('BENEFIT %'), None, style1),
            ('j', 1, 0, 'text', _('SALES'), None, style1),
            ('k', 1, 0, 'text', _('COST'), None, style1),
            ('l', 1, 0, 'text', _('BENEFIT'), None, style1),
            ('m', 1, 0, 'text', _('BENEFIT %'), None, style1),
            ('n', 1, 0, 'text', _('SALE TOTAL'), None, style1),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(self.ws, row_pos, row_data)
        return row_pos

    def _print_report_values(self, data, row_pos):
        for c_id in data:
            if c_id == 2:
                for user_id in data[c_id]:
                    val = data[c_id][user_id]
                    # user_name = self.pool.get('res.users').browse(self.cr,
                    #                                               1,
                    #                                               user_id).name
                    user_name = 'aaa'
                    sale = val['sale']
                    cost = val['cost']
                    benefit = sale - cost
                    benefit_per = (benefit * 100) / sale if sale else 0.0
                    c_specs = [
                        ('a', 1, 0, 'text', user_name, None, None),
                        ('b', 1, 0, 'text', str(round(sale, 2)), None, None),
                        ('c', 1, 0, 'text', str(round(cost, 2)), None, None),
                        ('d', 1, 0, 'text', str(round(benefit, 2)), None,
                         None),
                        ('e', 1, 0, 'text', str(round(benefit_per, 2)), None,
                         None),
                    ]
                    row_data = self.xls_row_template(c_specs,
                                                     [x[0] for x in c_specs])
                    row_pos = self.xls_write_row(self.ws, row_pos, row_data)
            else:
                for user_id in data[c_id]:
                    val = data[c_id][user_id]
                    # user_name = self.pool.get('res.users').browse(self.cr,
                    #                                               1,
                    #                                               user_id).name
                    user_name = 'bbbb'
                    sale = val['sale']
                    cost = val['cost']
                    benefit = sale - cost
                    benefit_per = (benefit * 100) / sale if sale else 0.0
                    c_specs = [
                        ('a', 1, 0, 'text', user_name, None, None),
                        ('b', 1, 0, 'text', None, None, None),
                        ('c', 1, 0, 'text', None, None, None),
                        ('d', 1, 0, 'text', None, None, None),
                        ('e', 1, 0, 'text', None, None, None),
                        ('f', 1, 0, 'text', None, None, None),
                        ('g', 1, 0, 'text', None, None, None),
                        ('h', 1, 0, 'text', None, None, None),
                        ('i', 1, 0, 'text', None, None, None),
                        ('j', 1, 0, 'text', str(round(sale, 2)), None, None),
                        ('k', 1, 0, 'text', str(round(cost, 2)), None, None),
                        ('l', 1, 0, 'text', str(round(benefit, 2)), None,
                         None),
                        ('m', 1, 0, 'text', str(round(benefit_per, 2)), None,
                         None),
                    ]
                    row_data = self.xls_row_template(c_specs,
                                                     [x[0] for x in c_specs])
                    row_pos = self.xls_write_row(self.ws, row_pos, row_data)
        return row_pos

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        # Initializations
        self.global_initializations(wb, _p, xlwt, _xs, objects, data)
        row_pos = 0
        # Report Title
        row_pos = self.print_title(objects, row_pos)
        # Print empty row to define column sizes
        row_pos = self.print_empty_row(row_pos)

        # Headers
        row_pos = self.print_header_titles(row_pos)

        # Values
        row_pos = self._print_report_values(data, row_pos)


ElnSalesmanSummaryXls('report.eln_salesman_summary_xls',
                      'eln.salesman.summary.xls.wzd',
                      parser=ElnSalesmanSummaryXlsParser)
