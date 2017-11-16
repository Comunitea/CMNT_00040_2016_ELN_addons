# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import xlwt
from openerp.addons.report_xls.report_xls import report_xls
from datetime import datetime
from openerp.report import report_sxw
from openerp.addons.report_xls.utils import rowcol_to_cell
from openerp.tools.translate import _


_ir_translation_name = 'eln_salesman_summary.xls'


class ElnSalesmanSummaryXlsParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ElnSalesmanSummaryXlsParser, self).__init__(cr, uid, name,
                                                          context=context)

        self.context = context
        self.localcontext.update({'datetime': datetime, '_': _})


class ElnSalesmanSummaryXls(report_xls):
    column_sizes = [30, 12, 12, 12, 7, 12, 12, 12, 7, 12, 12, 12, 7, 15]

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
        self.ws = wb.add_sheet(_("Resumen ventas"))
        self.nbr_columns = 14
        # Tytle style
        self.style_font12 = xlwt.easyxf(_xs['xls_title'] + _xs['center'])
        # Header Style
        self.style_bold_blue_center = xlwt.easyxf(
            _xs['bold'] + _xs['fill_blue'] + _xs['borders_all'] +
            _xs['center'])

    def print_title(self, objects, row_pos):
        start_date = datetime.strptime(objects.start_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        end_date = datetime.strptime(objects.end_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        report_name = ' '.join([_("Resumen ventas por representante:"),
                                start_date,
                                '-',
                                end_date])
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
            ('fghi', 4, 0, 'text', _('COMERCIAL VALQUIN (INDIRECTOS)'), None,
             style1),
            ('jklm', 4, 0, 'text', _('QUIVAL S.A'), None, style1),
            ('n', 1, 0, 'text', _('TOTAL'), None, style1),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(self.ws, row_pos, row_data)
        # PART 2
        c_specs = [
            ('a', 1, 0, 'text', _('VENDEDOR'), None, style1),
            ('b', 1, 0, 'text', _('VENTAS'), None, style1),
            ('c', 1, 0, 'text', _('COSTE'), None, style1),
            ('d', 1, 0, 'text', _('BENEFICIO'), None, style1),
            ('e', 1, 0, 'text', _('% BEN'), None, style1),
            ('f', 1, 0, 'text', _('VENTAS'), None, style1),
            ('g', 1, 0, 'text', _('COSTE'), None, style1),
            ('h', 1, 0, 'text', _('BENEFICIO'), None, style1),
            ('i', 1, 0, 'text', _('% BEN'), None, style1),
            ('j', 1, 0, 'text', _('VENTAS'), None, style1),
            ('k', 1, 0, 'text', _('COSTE'), None, style1),
            ('l', 1, 0, 'text', _('BENEFICIO'), None, style1),
            ('m', 1, 0, 'text', _('% BEN'), None, style1),
            ('n', 1, 0, 'text', _('TOTAL VENTAS'), None, style1),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(self.ws, row_pos, row_data)
        return row_pos

    def _get_values(self, by_company, group_col):
        sale = cost = benefit = benefit_per = 0.0
        if by_company.get(group_col, False):
            val = by_company[group_col]
            sale = val['sale']
            cost = val['cost']
            benefit = sale - cost
            benefit_per = (benefit * 100) / sale if sale else 0.0

            if group_col == 'indir_valquin':
                cost = benefit = benefit_per = 0.0

        return sale, cost, benefit, benefit_per

    def _print_report_values(self, data, row_pos):
        for salesman in data:
            by_company = data[salesman]
            c_specs = [('a', 1, 0, 'text', salesman, None, None)]
            sale_total = 0
            for c in ['valquin', 'indir_valquin', 'quival']:
                sale, cost, benefit, benefit_per = self._get_values(by_company,
                                                                    c)
                col1 = 'b' if c == 'valquin' else \
                    ('f' if c == 'indir_valquin' else 'j')
                col2 = 'c' if c == 'valquin' else \
                    ('g' if c == 'indir_valquin' else 'k')
                col3 = 'd' if c == 'valquin' else \
                    ('h' if c == 'indir_valquin' else 'l')
                col4 = 'e' if c == 'valquin' else \
                    ('i' if c == 'indir_valquin' else 'm')
                c_specs += [
                    (col1, 1, 0, 'number', sale, None, self.aml_cell_style_decimal),
                    (col2, 1, 0, 'number', cost, None, self.aml_cell_style_decimal),
                    (col3, 1, 0, 'number', benefit, None, self.aml_cell_style_decimal),
                    (col4, 1, 0, 'number', benefit_per, None, self.aml_cell_style_decimal)]
                sale_total += sale
            c_specs += [('n', 1, 0, 'number', sale_total, None, self.aml_cell_style_decimal)]
            row_data = self.xls_row_template(c_specs,
                                             [x[0] for x in c_specs])
            row_pos = self.xls_write_row(self.ws, row_pos, row_data)
        return row_pos

    def _print_totals(self, row_pos):
        init_pos = 4
        end_pos = row_pos - 2

        # VALQUIN TOTALS
        sale_start = rowcol_to_cell(init_pos, 1)
        sale_end = rowcol_to_cell(end_pos, 1)
        val_sales = 'SUM(' + sale_start + ':' + sale_end + ')'

        cost_start = rowcol_to_cell(init_pos, 2)
        cost_end = rowcol_to_cell(end_pos, 2)
        val_cost = 'SUM(' + cost_start + ':' + cost_end + ')'

        total_sale = rowcol_to_cell(row_pos, 1)
        total_cost = rowcol_to_cell(row_pos, 2)
        val_benefit = total_sale + '-' + total_cost

        total_benefit = rowcol_to_cell(row_pos, 3)
        val_benefit_per = total_benefit + '*' + '100' + '/' + total_sale

        # VALQUIN INDIRECT TOTALS
        sale_start = rowcol_to_cell(init_pos, 5)
        sale_end = rowcol_to_cell(end_pos, 5)
        in_val_sales = 'SUM(' + sale_start + ':' + sale_end + ')'

        # QUIVAL TOTALS
        sale_start = rowcol_to_cell(init_pos, 9)
        sale_end = rowcol_to_cell(end_pos, 9)
        qui_sales = 'SUM(' + sale_start + ':' + sale_end + ')'

        cost_start = rowcol_to_cell(init_pos, 10)
        cost_end = rowcol_to_cell(end_pos, 10)
        qui_cost = 'SUM(' + cost_start + ':' + cost_end + ')'

        total_sale = rowcol_to_cell(row_pos, 9)
        total_cost = rowcol_to_cell(row_pos, 10)
        qui_benefit = total_sale + '-' + total_cost

        total_benefit = rowcol_to_cell(row_pos, 11)
        qui_benefit_per = total_benefit + '*' + '100' + '/' + total_sale

        # TOTAL SALES
        sale_start = rowcol_to_cell(init_pos, 13)
        sale_end = rowcol_to_cell(end_pos, 13)
        total_total_sales = 'SUM(' + sale_start + ':' + sale_end + ')'

        c_specs = [
            ('a', 1, 0, 'text', _('TOTALES'), None, None),
            ('b', 1, 0, 'number', None, val_sales, self.aml_cell_style_decimal),
            ('c', 1, 0, 'number', None, val_cost, self.aml_cell_style_decimal),
            ('d', 1, 0, 'number', None, val_benefit, self.aml_cell_style_decimal),
            ('e', 1, 0, 'number', None, val_benefit_per, self.aml_cell_style_decimal),
            ('f', 1, 0, 'number', None, in_val_sales, self.aml_cell_style_decimal),
            ('g', 1, 0, 'number', None, None, self.aml_cell_style_decimal),
            ('h', 1, 0, 'number', None, None, self.aml_cell_style_decimal),
            ('i', 1, 0, 'number', None, None, self.aml_cell_style_decimal),
            ('j', 1, 0, 'number', None, qui_sales, self.aml_cell_style_decimal),
            ('k', 1, 0, 'number', None, qui_cost, self.aml_cell_style_decimal),
            ('l', 1, 0, 'number', None, qui_benefit, self.aml_cell_style_decimal),
            ('m', 1, 0, 'number', None, qui_benefit_per, self.aml_cell_style_decimal),
            ('n', 1, 0, 'number', None, total_total_sales, self.aml_cell_style_decimal),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
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

        # Print empty row to define column sizes
        row_pos = self.print_empty_row(row_pos)

        # Totals
        row_pos = self._print_totals(row_pos)


ElnSalesmanSummaryXls('report.eln_salesman_summary_xls',
                      'eln.salesman.summary.xls.wzd',
                      parser=ElnSalesmanSummaryXlsParser)
