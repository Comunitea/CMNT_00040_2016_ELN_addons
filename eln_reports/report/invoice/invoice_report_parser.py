# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import registry
from openerp.addons import jasper_reports


def parser(cr, uid, ids, data, context):
    invoice_obj = registry(cr.dbname).get('account.invoice')
    invoice_ids = invoice_obj.browse(cr, uid, ids, context)
    language = list(set(invoice_ids.mapped('partner_id.lang')))
    parameters = {}
    name = 'report.invoice_report_jasper'
    model = 'account.invoice'
    data_source = 'model'
    if len(language) == 1:
        context['lang'] = language[0]
    return { 
        'ids': ids, 
        'name': name, 
        'model': model, 
        'records': [], 
        'data_source': data_source,
        'parameters': parameters,
    }


jasper_reports.report_jasper('report.invoice_report_jasper', 'account.invoice', parser)
