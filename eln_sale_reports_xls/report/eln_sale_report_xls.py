# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import xlwt
from openerp.addons.report_xls.report_xls import report_xls
from datetime import datetime
from openerp.report import report_sxw
# from openerp.addons.report_xls.utils import _render
from openerp.addons.report_xls.utils import rowcol_to_cell
from openerp.tools.translate import _


_ir_translation_name = 'eln_sale_report.xls'


class ElnSaleReportXlsParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ElnSaleReportXlsParser, self).__init__(cr, uid, name,
                                                     context=context)

        self.context = context
        self.localcontext.update({'datetime': datetime, '_': _})


class ElnSaleReportXls(report_xls):
    column_sizes = [60, 8, 8, 8, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12]

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
        self.ws = wb.add_sheet(_("Informe diario de ventas"))
        self.nbr_columns = 14
        # Tytle style
        self.style_font12 = xlwt.easyxf(_xs['xls_title'] + _xs['center'])
        # Header Style
        self.style_bold_blue_center = xlwt.easyxf(
            _xs['bold'] + _xs['fill_blue'] + _xs['borders_all'] +
            _xs['center'])
        self.report_date = objects.date

    def print_title(self, objects, row_pos):
        date = objects.date
        date_split = date.split('-')
        year = date_split[0]
        months = {
            '01': _('ENERO'),
            '02': _('FEBRERO'),
            '03': _('MARZO'),
            '04': _('ABRIL'),
            '05': _('MAYO'),
            '06': _('JUNIO'),
            '07': _('JULIO'),
            '08': _('AGOSTO'),
            '09': _('SEPTIEMBRE'),
            '10': _('OCTUBRE'),
            '11': _('NOVIEMBRE'),
            '12': _('DICIEMBRE'),
        }
        month = months[date_split[1]]
        report_date = datetime.strptime(objects.date, '%Y-%m-%d').strftime('%d/%m/%Y')
        report_name = ' - '.join(["INFORME DIARIO DE VENTAS", month + ' ' +
                                 year, '(A FECHA:' + report_date + ')'])
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
            ('b', 3, 0, 'text', None, None, None),
            ('c', 5, 0, 'text', _('EUROS'), None, style1),
            ('d', 5, 0, 'text', _('KILOS'), None, style1),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(self.ws, row_pos, row_data)
        # PART 2
        c_specs = [
            ('a', 1, 0, 'text', None, None, None),
            ('b', 3, 0, 'text', _('% RENT'), None, style1),
            ('c', 2, 0, 'text', _('ACUMULADOS'), None, style1),
            ('d', 1, 0, 'text', _('DEL DÍA'), None, style1),
            ('e', 1, 0, 'text', _('AÑO ANT.'), None, style1),
            ('f', 1, 0, 'text', _('PRESUP.'), None, style1),
            ('g', 2, 0, 'text', _('ACUMULADOS'), None, style1),
            ('h', 1, 0, 'text', _('DEL DÍA'), None, style1),
            ('i', 1, 0, 'text', _('AÑO ANT.'), None, style1),
            ('j', 1, 0, 'text', _('PRESUP.'), None, style1),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(self.ws, row_pos, row_data)
        # PART 2
        c_specs = [
            ('a', 1, 0, 'text', _('CUENTA ANALÍTICA'), None, style1),
            ('b', 1, 0, 'text', _('ACTUAL'), None, style1),
            ('c', 1, 0, 'text', _('ANT.'), None, style1),
            ('d', 1, 0, 'text', _('A. ANT.'), None, style1),
            ('e', 1, 0, 'text', _('ACTUALES'), None, style1),
            ('f', 1, 0, 'text', _('ANTERIORES'), None, style1),
            ('g', 1, 0, 'text', None, None, style1),
            ('h', 1, 0, 'text', None, None, style1),
            ('i', 1, 0, 'text', None, None, style1),
            ('j', 1, 0, 'text', _('ACTUALES'), None, style1),
            ('k', 1, 0, 'text', _('ANTERIORES'), None, style1),
            ('l', 1, 0, 'text', None, None, style1),
            ('m', 1, 0, 'text', None, None, style1),
            ('n', 1, 0, 'text', None, None, style1),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(self.ws, row_pos, row_data)
        return row_pos

    def _print_report_values(self, data, row_pos):
        for acc_name in sorted(data):
            val = data[acc_name]
            margin = ((val['base'] - val['p_price']) * 100)\
                / val['base'] if val['base'] else 0.0
            ld_margin = ((val['ld_base'] - val['ld_p_price'])) * 100 \
                / val['ld_base'] if val['ld_base'] else 0.0
            ly_margin = ((val['ly_base'] - val['ly_p_price'])) * 100 \
                / val['ly_base'] if val['ly_base'] else 0.0
            c_specs = [
                ('a', 1, 0, 'text', val['name'], None, self.aml_cell_style),
                ('b', 1, 0, 'number', round(margin, 2), None, self.aml_cell_style_decimal),
                ('c', 1, 0, 'number', round(ld_margin, 2), None, self.aml_cell_style_decimal),
                ('d', 1, 0, 'number', round(ly_margin, 2), None, self.aml_cell_style_decimal),
                ('e', 1, 0, 'number', round(val['base'], 2), None, self.aml_cell_style_decimal),
                ('f', 1, 0, 'number', round(val['ld_base'], 2), None, self.aml_cell_style_decimal),
                ('g', 1, 0, 'number', round(val['base'] - val['ld_base'], 2), None, self.aml_cell_style_decimal),
                ('h', 1, 0, 'number', round(val['ly_base'], 2), None, self.aml_cell_style_decimal),
                ('i', 1, 0, 'number', round(val['quot1'], 2), None, self.aml_cell_style_decimal),
                ('j', 1, 0, 'number', round(val['kg'], 2), None, self.aml_cell_style_decimal),
                ('k', 1, 0, 'number', round(val['ld_kg'], 2), None, self.aml_cell_style_decimal),
                ('l', 1, 0, 'number', round(val['kg'] - val['ld_kg'], 2), None, self.aml_cell_style_decimal),
                ('m', 1, 0, 'number', round(val['ly_kg'], 2), None, self.aml_cell_style_decimal),
                ('n', 1, 0, 'number', round(val['quot2'], 2), None, self.aml_cell_style_decimal),
            ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(self.ws, row_pos, row_data)
        return row_pos

    def _print_totals(self, data, row_pos):
        init_pos = 5
        end_pos = row_pos - 2
        
        # Calculamos importes totales y coste total para calcular % rent total
        base, ld_base, ly_base = 0, 0, 0
        cost, ld_cost, ly_cost = 0, 0, 0
        for acc_name in data:
            val = data[acc_name]
            base += val['base'] if val['base'] else 0.0
            ld_base += val['ld_base'] if val['ld_base'] else 0.0
            ly_base += val['ly_base'] if val['ly_base'] else 0.0
            cost += val['p_price'] if val['p_price'] else 0.0
            ld_cost += val['ld_p_price'] if val['ld_p_price'] else 0.0
            ly_cost += val['ly_p_price'] if val['ly_p_price'] else 0.0
        margin = ((base - cost) * 100) / base if base else 0.0
        ld_margin = ((ld_base - ld_cost) * 100) / ld_base if ld_base else 0.0
        ly_margin = ((ly_base - ly_cost) * 100) / ly_base if ly_base else 0.0

        # RENT
        val_margin = round(margin, 2)
        val_ld_margin = round(ld_margin, 2)
        val_ly_margin = round(ly_margin, 2)
        
        # EUROS - KILOS
        val_sum = {}
        for i in range(4, 14): 
            cell_start = rowcol_to_cell(init_pos, i)
            cell_end = rowcol_to_cell(end_pos, i)
            val_sum[i] = 'SUM(' + cell_start + ':' + cell_end + ')'

        c_specs = [
            ('a', 1, 0, 'text', _('TOTALES'), None, self.aml_cell_style_decimal),
            ('b', 1, 0, 'number', val_margin, None, self.aml_cell_style_decimal),
            ('c', 1, 0, 'number', val_ld_margin, None, self.aml_cell_style_decimal),
            ('d', 1, 0, 'number', val_ly_margin, None, self.aml_cell_style_decimal),
            ('e', 1, 0, 'number', None, val_sum[4], self.aml_cell_style_decimal),
            ('f', 1, 0, 'number', None, val_sum[5], self.aml_cell_style_decimal),
            ('g', 1, 0, 'number', None, val_sum[6], self.aml_cell_style_decimal),
            ('h', 1, 0, 'number', None, val_sum[7], self.aml_cell_style_decimal),
            ('i', 1, 0, 'number', None, val_sum[8], self.aml_cell_style_decimal),
            ('j', 1, 0, 'number', None, val_sum[9], self.aml_cell_style_decimal),
            ('k', 1, 0, 'number', None, val_sum[10], self.aml_cell_style_decimal),
            ('l', 1, 0, 'number', None, val_sum[11], self.aml_cell_style_decimal),
            ('m', 1, 0, 'number', None, val_sum[12], self.aml_cell_style_decimal),
            ('n', 1, 0, 'number', None, val_sum[13], self.aml_cell_style_decimal),
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
        row_pos = self._print_totals(data, row_pos)


ElnSaleReportXls('report.eln_sale_report_xls',
                 'eln.sale.report.xls.wzd',
                 parser=ElnSaleReportXlsParser)
