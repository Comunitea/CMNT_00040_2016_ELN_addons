# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    Copyright (C) 2015- Comunitea Servicios Tecnologicos All Rights Reserved
#    $Kiko Sánchez$ <kiko@comunitea.com>
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
import time

from odoo.report import report_sxw
import calendar

class parser_report_budget(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(parser_report_budget, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_lines': self.get_lines,
        })
        self.context = context

    def _get_form_param(self, param, data, default=False):
        return data.get('form', {}).get(param, default)

    def _exec_query(self, date, acc_ids):

        if acc_ids and acc_ids[0] and date:
            where_date = ''
            where_date += " AND l.date <= %s"
            where_clause_args = acc_ids
            where_clause_args += [date]

            self.cr.execute("""
            SELECT COALESCE(SUM(l.amount),0) AS balance
            FROM account_analytic_account a
                LEFT JOIN account_analytic_line l ON (a.id = l.account_id)
                WHERE a.id IN %s """ + where_date + """""", where_clause_args)
            return self.cr.fetchall()[0][0]

        return


    def _get_real_amount_by_to_date(self, month, date, acc_ids):

        if month and date:

            if len(str(month)) == 1:
                month = "0"+str(month)
            else:
                month = str(month)

            first_day, last_day = calendar.monthrange(int(date[:4]),int(month))
            complet_last_date = date[:4]+"-"+month+"-"+str(last_day)
            complet_first_date = date[:4]+"-"+month+"-"+str(first_day)

            if date > complet_last_date:
                return self._exec_query(complet_last_date,acc_ids)
            elif date < complet_last_date and date > complet_first_date:
                return self._exec_query(date, acc_ids)
            else:
                return 0.00

    def set_context(self, objects, data, ids, report_type=None):
        get_items = self._get_form_param('get_items', data)
        child_ids = []
        objects = []
        version = self.pool.get('budget.version').browse(self.cr, self.uid, data['form']['version_id'][0])
        if data['form']['date_to']:
            todate = data['form']['date_to']
        else:
            todate = time.strftime("%Y-%m-%d")
        items = False

        if data['form']['item_id']:
            items = [self.pool.get('budget.item').browse(self.cr, self.uid, data['form']['item_id'][0])]
        elif version.budget_id.budget_item_id and version.budget_id.budget_item_id.children_ids:
            items = version.budget_id.budget_item_id.children_ids

        if items:
            for item in items:
                where_date = ''
                where_clause_args = ''
                prev_amount = 0.0
                real_amount = 0.0
                jan_amount = 0.0
                feb_amount = 0.0
                mar_amount = 0.0
                apr_amount = 0.0
                may_amount = 0.0
                jun_amount = 0.0
                jul_amount = 0.0
                aug_amount = 0.0
                sep_amount = 0.0
                oct_amount = 0.0
                nov_amount = 0.0
                dec_amount = 0.0
                lines = self.pool.get('budget.line').search(self.cr, self.uid, [('budget_version_id','=',version.id), ('budget_item_id','=',item.id)])
                if lines:
                    self.cr.execute('''select
                    sum(jan_amount),sum(feb_amount),
                    sum(mar_amount),sum(apr_amount),
                    sum(may_amount),sum(jun_amount),
                    sum(jul_amount),sum(aug_amount),
                    sum(sep_amount),sum(oct_amount),
                    sum(nov_amount),sum(dec_amount),
                    sum(amount) from budget_line
                    where id in %s''', ([tuple(lines)]))

                    r = self.cr.fetchall()[0]
                    prev_amount = r[12]
                    jan_amount = r[0]
                    feb_amount = r[1]
                    mar_amount = r[2]
                    apr_amount = r[3]
                    may_amount = r[4]
                    jun_amount = r[5]
                    jul_amount = r[6]
                    aug_amount = r[7]
                    sep_amount = r[8]
                    oct_amount = r[9]
                    nov_amount = r[10]
                    dec_amount = r[11]

                acc = self.pool.get('account.analytic.account').search(self.cr, self.uid, [('code','=',item.code)])

                if acc:

                    child_ids = tuple(self.pool.get('account.analytic.account').search(self.cr, self.uid, [('parent_id', 'child_of', acc)]))
                    where_date += " AND l.date <= %s"
                    where_clause_args = [tuple(child_ids)]
                    where_clause_args += [todate]

                    self.cr.execute("""
              SELECT COALESCE(SUM(l.amount),0) AS balance
              FROM account_analytic_account a
                  LEFT JOIN account_analytic_line l ON (a.id = l.account_id)
              WHERE a.id IN %s
              """ + where_date + """""", where_clause_args)

                    real_amount = self.cr.fetchall()[0][0]

                item.name = item.name
                item.jan_amount = jan_amount
                item.feb_amount = feb_amount
                item.mar_amount = mar_amount
                item.apr_amount = apr_amount
                item.may_amount = may_amount
                item.jun_amount = jun_amount
                item.jul_amount = jul_amount
                item.aug_amount = aug_amount
                item.sep_amount = sep_amount
                item.oct_amount = oct_amount
                item.nov_amount = nov_amount
                item.dec_amount = dec_amount
                item.jan_amount_real = self._get_real_amount_by_to_date(1, todate, [tuple(child_ids)]) or 0.0
                item.feb_amount_real = self._get_real_amount_by_to_date(2, todate, [tuple(child_ids)]) or 0.0
                item.mar_amount_real = self._get_real_amount_by_to_date(3, todate, [tuple(child_ids)]) or 0.0
                item.apr_amount_real = self._get_real_amount_by_to_date(4, todate, [tuple(child_ids)]) or 0.0
                item.may_amount_real = self._get_real_amount_by_to_date(5, todate, [tuple(child_ids)]) or 0.0
                item.jun_amount_real = self._get_real_amount_by_to_date(6, todate, [tuple(child_ids)]) or 0.0
                item.jul_amount_real = self._get_real_amount_by_to_date(7, todate, [tuple(child_ids)]) or 0.0
                item.aug_amount_real = self._get_real_amount_by_to_date(8, todate, [tuple(child_ids)]) or 0.0
                item.sep_amount_real = self._get_real_amount_by_to_date(9, todate, [tuple(child_ids)]) or 0.0
                item.oct_amount_real = self._get_real_amount_by_to_date(10, todate, [tuple(child_ids)]) or 0.0
                item.nov_amount_real = self._get_real_amount_by_to_date(11, todate, [tuple(child_ids)]) or 0.0
                item.dec_amount_real = self._get_real_amount_by_to_date(12, todate, [tuple(child_ids)]) or 0.0
                item.prev_amount = prev_amount
                item.real_amount = real_amount

                item.jandiff = float(round(((item.jan_amount_real - item.jan_amount) / (item.prev_amount or 1.0)) * 100, 2))
                item.febdiff = float(round(((item.feb_amount_real - item.feb_amount) / (item.prev_amount or 1.0)) * 100, 2))
                item.mardiff = float(round(((item.mar_amount_real - item.mar_amount) / (item.prev_amount or 1.0)) * 100, 2))
                item.aprdiff = float(round(((item.apr_amount_real - item.apr_amount) / (item.prev_amount or 1.0)) * 100, 2))
                item.maydiff = float(round(((item.may_amount_real - item.may_amount) / (item.prev_amount or 1.0)) * 100, 2))
                item.jundiff = float(round(((item.jun_amount_real - item.jun_amount) / (item.prev_amount or 1.0)) * 100, 2))
                item.juldiff = float(round(((item.jul_amount_real - item.jul_amount) / (item.prev_amount or 1.0)) * 100, 2))
                item.augdiff = float(round(((item.aug_amount_real - item.aug_amount) / (item.prev_amount or 1.0)) * 100, 2))
                item.sepdiff = float(round(((item.sep_amount_real - item.sep_amount) / (item.prev_amount or 1.0)) * 100, 2))
                item.octdiff = float(round(((item.oct_amount_real - item.oct_amount) / (item.prev_amount or 1.0)) * 100, 2))
                item.novdiff = float(round(((item.nov_amount_real - item.nov_amount) / (item.prev_amount or 1.0)) * 100, 2))
                item.decdiff = float(round(((item.dec_amount_real - item.dec_amount) / (item.prev_amount or 1.0)) * 100, 2))
                item.analytic_lines = self.get_analytic_lines(data, item.id)

                objects.append(item)

        return super(parser_report_budget, self).set_context(objects, data, ids,
                                                            report_type=report_type)

    def get_analytic_lines(self, data, item):
        alines = []
        avisited_lines = []

        version = self.pool.get('budget.version').browse(self.cr, self.uid, data['form']['version_id'][0])
        if data['form']['date_to']:
            todate = data['form']['date_to']
        else:
            todate = time.strftime("%Y-%m-%d")

        self.cr.execute('''select distinct(analytic_account_id) from budget_line where budget_item_id = %s''', (item,))
        accs = self.cr.fetchall()
        if accs and accs[0] and accs[0][0]:
            accs = list(x[0] for x in accs)

            for ac in self.pool.get('account.analytic.account').browse(self.cr, self.uid, accs):
                where_date = ''
                where_clause_args = ''
                self.cr.execute('''select
                    sum(jan_amount),sum(feb_amount),
                    sum(mar_amount),sum(apr_amount),
                    sum(may_amount),sum(jun_amount),
                    sum(jul_amount),sum(aug_amount),
                    sum(sep_amount),sum(oct_amount),
                    sum(nov_amount),sum(dec_amount),
                    sum(amount) from budget_line
                    where budget_item_id = %s and
                    analytic_account_id = %s''',(item,ac.id,))
                aclines = self.cr.fetchall()[0]
                where_date += " AND l.date <= %s"
                where_clause_args = [str(ac.id)]
                where_clause_args += [todate]

                self.cr.execute("""
              SELECT COALESCE(SUM(l.amount),0) AS balance
              FROM account_analytic_account a
                  LEFT JOIN account_analytic_line l ON (a.id = l.account_id)
              WHERE a.id = %s
              """ + where_date + """""", where_clause_args)

                real_amount = self.cr.fetchall()[0][0]

                ac.name = ac.name
                ac.jan_amount = aclines[0]
                ac.feb_amount = aclines[1]
                ac.mar_amount = aclines[2]
                ac.apr_amount = aclines[3]
                ac.may_amount = aclines[4]
                ac.jun_amount = aclines[5]
                ac.jul_amount = aclines[6]
                ac.aug_amount = aclines[7]
                ac.sep_amount = aclines[8]
                ac.oct_amount = aclines[9]
                ac.nov_amount = aclines[10]
                ac.dec_amount = aclines[11]
                ac.prev_amount = aclines[12]
                ac.jan_amount_real = self._get_real_amount_by_to_date(1, todate, [(ac.id,)])
                ac.feb_amount_real = self._get_real_amount_by_to_date(2, todate, [(ac.id,)])
                ac.mar_amount_real = self._get_real_amount_by_to_date(3, todate, [(ac.id,)])
                ac.apr_amount_real = self._get_real_amount_by_to_date(4, todate, [(ac.id,)])
                ac.may_amount_real = self._get_real_amount_by_to_date(5, todate, [(ac.id,)])
                ac.jun_amount_real = self._get_real_amount_by_to_date(6, todate, [(ac.id,)])
                ac.jul_amount_real = self._get_real_amount_by_to_date(7, todate, [(ac.id,)])
                ac.aug_amount_real = self._get_real_amount_by_to_date(8, todate, [(ac.id,)])
                ac.sep_amount_real = self._get_real_amount_by_to_date(9, todate, [(ac.id,)])
                ac.oct_amount_real = self._get_real_amount_by_to_date(10, todate, [(ac.id,)])
                ac.nov_amount_real = self._get_real_amount_by_to_date(11, todate, [(ac.id,)])
                ac.dec_amount_real = self._get_real_amount_by_to_date(12, todate, [(ac.id,)])
                ac.real_amount = real_amount

                ac.jandiff = float(round(((ac.jan_amount_real - ac.jan_amount) / ac.prev_amount) * 100, 2))
                ac.febdiff = float(round(((ac.feb_amount_real - ac.feb_amount) / ac.prev_amount) * 100, 2))
                ac.mardiff = float(round(((ac.mar_amount_real - ac.mar_amount) / ac.prev_amount) * 100, 2))
                ac.aprdiff = float(round(((ac.apr_amount_real - ac.apr_amount) / ac.prev_amount) * 100, 2))
                ac.maydiff = float(round(((ac.may_amount_real - ac.may_amount) / ac.prev_amount) * 100, 2))
                ac.jundiff = float(round(((ac.jun_amount_real - ac.jun_amount) / ac.prev_amount) * 100, 2))
                ac.juldiff = float(round(((ac.jul_amount_real - ac.jul_amount) / ac.prev_amount) * 100, 2))
                ac.augdiff = float(round(((ac.aug_amount_real - ac.aug_amount) / ac.prev_amount) * 100, 2))
                ac.sepdiff = float(round(((ac.sep_amount_real - ac.sep_amount) / ac.prev_amount) * 100, 2))
                ac.octdiff = float(round(((ac.oct_amount_real - ac.oct_amount) / ac.prev_amount) * 100, 2))
                ac.novdiff = float(round(((ac.nov_amount_real - ac.nov_amount) / ac.prev_amount) * 100, 2))
                ac.decdiff = float(round(((ac.dec_amount_real - ac.dec_amount) / ac.prev_amount) * 100, 2))
                #self._get_real_amount_by_to_date(1, todate, [tuple(child_ids)])
                ac.product_lines = self.get_lines(data, item, ac.id)

                alines.append(ac)

        return alines

    def _exec_query_product_lines(self, date, acc_ids, product):
        if acc_ids and date:
            if product == False:
                self.cr.execute("""
            SELECT COALESCE(SUM(l.amount),0) AS balance
            FROM account_analytic_account a
                LEFT JOIN account_analytic_line l ON (a.id = l.account_id)
                WHERE a.id = """ + str(acc_ids) + """ AND l.date <= '""" + date + """'""")
            else:
                self.cr.execute("""
            SELECT COALESCE(SUM(l.amount),0) AS balance
            FROM account_analytic_account a
                LEFT JOIN account_analytic_line l ON (a.id = l.account_id)
                WHERE product_id = """ + str(product) + """ and a.id = """ + str(acc_ids) + """ AND l.date <= '""" + date + """'""")


            return self.cr.fetchall()[0][0]

        return


    def _get_real_amount_by_to_date_product_lines(self, month, date, acc_ids, product):

        if month and date:

            if len(str(month)) == 1:
                month = "0"+str(month)
            else:
                month = str(month)

            first_day, last_day = calendar.monthrange(int(date[:4]),int(month))
            complet_last_date = date[:4]+"-"+month+"-"+str(last_day)
            complet_first_date = date[:4]+"-"+month+"-"+str(first_day)

            if date > complet_last_date:
                return self._exec_query_product_lines(complet_last_date,acc_ids, product)
            elif date < complet_last_date and date > complet_first_date:
                return self._exec_query_product_lines(date, acc_ids, product)
            else:
                return 0.00

    def get_lines(self, data, item, account):

        """
        Returns all the data needed for the report lines
        """
        blines = []
        version = self.pool.get('budget.version').browse(self.cr, self.uid, data['form']['version_id'][0])
        if data['form']['date_to']:
            todate = data['form']['date_to']
        else:
            todate = time.strftime("%Y-%m-%d")

        lines = self.pool.get('budget.line').search(self.cr, self.uid, [('budget_version_id','=',version.id),('budget_item_id','=',item), ('analytic_account_id', '=', account)])

        if lines:
            for line in self.pool.get('budget.line').browse(self.cr, self.uid, lines):
                line.name = line.product_id and line.product_id.default_code or line.name
                line.prev_amount = line.amount
                line.jan_amount = line.jan_amount
                line.feb_amount = line.feb_amount
                line.mar_amount = line.mar_amount
                line.apr_amount = line.apr_amount
                line.may_amount = line.may_amount
                line.jun_amount = line.jun_amount
                line.jul_amount = line.jul_amount
                line.aug_amount = line.aug_amount
                line.sep_amount = line.sep_amount
                line.oct_amount = line.oct_amount
                line.nov_amount = line.nov_amount
                line.dec_amount = line.dec_amount
                if line.product_id:
                    product = line.product_id.id
                else:
                    product = False
                line.jan_amount_real = self._get_real_amount_by_to_date_product_lines(1, todate, account, product)
                line.feb_amount_real = self._get_real_amount_by_to_date_product_lines(2, todate, account, product)
                line.mar_amount_real = self._get_real_amount_by_to_date_product_lines(3, todate, account, product)
                line.apr_amount_real = self._get_real_amount_by_to_date_product_lines(4, todate, account, product)
                line.may_amount_real = self._get_real_amount_by_to_date_product_lines(5, todate, account, product)
                line.jun_amount_real = self._get_real_amount_by_to_date_product_lines(6, todate, account, product)
                line.jul_amount_real = self._get_real_amount_by_to_date_product_lines(7, todate, account, product)
                line.aug_amount_real = self._get_real_amount_by_to_date_product_lines(8, todate, account, product)
                line.sep_amount_real = self._get_real_amount_by_to_date_product_lines(9, todate, account, product)
                line.oct_amount_real = self._get_real_amount_by_to_date_product_lines(10, todate, account, product)
                line.nov_amount_real = self._get_real_amount_by_to_date_product_lines(11, todate, account, product)
                line.dec_amount_real = self._get_real_amount_by_to_date_product_lines(12, todate, account, product)

                line.jandiff = float(round(((line.jan_amount_real - line.jan_amount) / line.prev_amount) * 100, 2))
                line.febdiff = float(round(((line.feb_amount_real - line.feb_amount) / line.prev_amount) * 100, 2))
                line.mardiff = float(round(((line.mar_amount_real - line.mar_amount) / line.prev_amount) * 100, 2))
                line.aprdiff = float(round(((line.apr_amount_real - line.apr_amount) / line.prev_amount) * 100, 2))
                line.maydiff = float(round(((line.may_amount_real - line.may_amount) / line.prev_amount) * 100, 2))
                line.jundiff = float(round(((line.jun_amount_real - line.jun_amount) / line.prev_amount) * 100, 2))
                line.juldiff = float(round(((line.jul_amount_real - line.jul_amount) / line.prev_amount) * 100, 2))
                line.augdiff = float(round(((line.aug_amount_real - line.aug_amount) / line.prev_amount) * 100, 2))
                line.sepdiff = float(round(((line.sep_amount_real - line.sep_amount) / line.prev_amount) * 100, 2))
                line.octdiff = float(round(((line.oct_amount_real - line.oct_amount) / line.prev_amount) * 100, 2))
                line.novdiff = float(round(((line.nov_amount_real - line.nov_amount) / line.prev_amount) * 100, 2))
                line.decdiff = float(round(((line.dec_amount_real - line.dec_amount) / line.prev_amount) * 100, 2))

                line.real_amount = self._get_real_amount_by_to_date_product_lines(12, todate, [(account,)], product)

                blines.append(line)

        return blines

report_sxw.report_sxw('report.report.budget.report.webkit', 'report.budget', 'budget/report/report_budget_webkit.mako', parser=parser_report_budget, header=False)
