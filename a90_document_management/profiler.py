# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#    $Marta Vázquez Rodríguez$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import jasper_reports
import openerp.pooler as pooler
from openerp.tools.translate import _
import time
import base64

if 'old_create' not in dir(jasper_reports.jasper_report.report_jasper.create):
    jasper_reports.jasper_report.report_jasper.old_create = jasper_reports.jasper_report.report_jasper.create

def create(self, cr, uid, ids, data, context=None):
        # import ipdb; ipdb.set_trace()
        if context is None:
            context = {}

        data_binary = self.old_create(cr, uid, ids, data, context=context)
        expedient_document_id = False
        at = []
        continuate = False
        last = False
        state = False
        attachment_id = False

        #if data.get('model',False) and data.get('id',False):
        if context.get('active_model',False) and context.get('active_ids', []):
            #obj = pooler.get_pool(cr.dbname).get(data['model']).browse(cr, uid, data['id'])
            obj = pooler.get_pool(cr.dbname).get(context['active_model']).browse(cr, uid, context['active_ids'][0])
            if 'x_expedient_id' in obj._columns:
                if obj.x_expedient_id and obj.x_expedient_id.expedient_document:
                    for report in obj.x_expedient_id.expedient_document:
                        if report.attach_mode and report.attach_mode == 'printing' \
                        and report.ir_act_report_xml_id and report.ir_act_report_xml_id.model \
                        and report.ir_act_report_xml_id.model == context['active_model'] \
                        and report.ir_act_report_xml_id.report_name == (self.name).split("report.")[1]:
                            if report.valid_last == True:
                                last = True
                            else:
                                last = False
                            continuate = True
                            expedient_document_id = report.id
                            break
            if continuate == True:
                if obj.x_expedient_id.attachment_ids:
                    for attach in obj.x_expedient_id.attachment_ids:
                        if attach.res_model == context['active_model'] and attach.res_id == context['active_ids'][0]:
                            if attach.name == self.name:
                                if last == False:
                                    at.append(attach.id)
                                else:
                                    attach.unlink()
                            else:
                                at.append(attach.id)
                        else:
                            at.append(attach.id)
                obj_current = pooler.get_pool(cr.dbname).get(context['active_model']).browse(cr, uid, context['active_ids'][0])
                if obj.x_expedient_id.model_ids:
                    for model in obj.x_expedient_id.model_ids:
                        if model.ir_model and model.ir_model.model and model.ir_model.model == context['active_model']:
                            if model.cancellation and model.cancellation == obj_current.state:
                                state = True
                if obj.x_expedient_id.origin_model and obj.x_expedient_id.cancellation and obj.x_expedient_id.cancellation == obj_current.state:
                    state = True

                if state == False:
                    attachment_id = pooler.get_pool(cr.dbname).get('ir.attachment').create(cr, uid, {
                        'res_id': context['active_ids'][0],
                        'res_model':context['active_model'],
                        'name': self.name,
                        'datas': base64.encodestring(data_binary[0]),
                        'datas_fname': obj.name + '_' + time.strftime("%Y-%m-%d_%H%M%S") + '.pdf',
                        'description': _('Attachment of ' + context['active_model'] + '-' + str(context['active_ids'][0])),
                        'type2': (self.name).split("report.")[1],
                        'expedient_document_id': expedient_document_id and expedient_document_id or False,
                        'type': 'binary'
                        }, context)

                if attachment_id:
                    at.append(attachment_id)
                if at:
                    pooler.get_pool(cr.dbname).get('expedient').write(cr, uid, [obj.x_expedient_id.id], {'attachment_ids': [(6,0,at)]})
                at = []
        return data_binary

#override create method of class report_jasper
jasper_reports.jasper_report.report_jasper.create = create
