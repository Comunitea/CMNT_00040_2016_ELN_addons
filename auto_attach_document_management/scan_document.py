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
from tools.translate import _
from osv import osv, fields
from NanScan.Template import *
from NanScan.Document import *
from NanScan.Recognizer import *
from NanScan.Ocr import *
import netsvc

class ir_attachment(osv.osv):
    
    _inherit = "ir.attachment"
    
    _columns = {
        'annex': fields.boolean("Annex", readonly=True)
    }
    
ir_attachment()

class scan_document(osv.osv):

    _inherit = 'scan.document'
    _columns = {
        'state': fields.selection( [
            ('pending', 'Pending'), ('analyzing', 'Analyzing'),
            ('analyzed', 'Analyzed'), ('verified', 'Verified'),
            ('processing', 'Processing'), ('processed', 'Processed'),
            ('filed','Filed'),
            ('exception','Exception')],
            'State', required=True, readonly=True ),
        'counter': fields.integer('Counter'),
        'pdf_type': fields.boolean("Pdf", readonly=True),
        'except_state': fields.boolean("Exception", readonly=True),
        'annex': fields.boolean('Annex', readonly=True)
    }
    def analyze_document(self, cr, uid, ids, context=None):
        
        if not ids:
            ids = self.search(cr, uid, [('state','=','pending')])
        res = super(scan_document, self).analyze_document(cr,
            uid, ids, context)
        ids2 = list(ids)
        except_ids = []
        for document in self.browse(cr, uid, ids, context):
            if document.property_ids:
                prop = document.property_ids[0]
                
                if prop.value:
                    barcode = prop.value
                    barcode = barcode.split('/')
                    model = barcode[0]
                    cur = self.pool.get(model.split(',')[0]).search(cr, uid, [('id','=',int(model.split(',')[1]))])
                    if cur:
                        cur_obj = self.pool.get(model.split(',')[0]).browse(cr, uid, cur[0])
                        if 'x_expedient_id' not in cur_obj._columns or not cur_obj.x_expedient_id:
                            message = u"Document " + document.name + u" printed from the model " + model.split(',')[0] + u" with id " + model.split(',')[1] + u" has no associated expedient."
                            self.pool.get('scan.document').log_expedient(cr, uid, document.id, message, False, False, context=context)
                            for x in ids2:
                                if x == document.id:
                                    ids2.remove(x)
                                    except_ids.append(x)
                            continue
                        if len(barcode) < 2 :
                            document.write({'annex': True})
                            attachs = self.pool.get('ir.attachment').search(cr, uid, [('res_id','=',document.id),('res_model','=','scan.document')])
                            if attachs:
                                attach_obj = self.pool.get('ir.attachment').browse(cr, uid, attachs[0])
                                attachment_model = self.pool.get('ir.attachment').create(cr, uid, {
                                        'res_id': int(model.split(',')[1]),
                                        'res_model': model.split(',')[0],
                                        'name': attach_obj.name,
                                        'datas': attach_obj.datas,
                                        'datas_fname':attach_obj.datas_fname,
                                        'description': _('Annex Generated from document management'),
                                        'type': 'binary',
                                        'type2':False,
                                        'annex': True
                                    }, context)
                                    
            else:
                if document.counter:
                    counter = document.counter + 1
                else:
                    counter = 1
                self.pool.get('scan.document').write(cr, uid, document.id, {'counter': counter,'task': (document.task or u"") + u'\nCould not recognize DataMatrix.'})
                document = self.pool.get('scan.document').browse(cr, uid, document.id)
                if document.scan_queue_id and document.scan_queue_id.no_attempts:
                    if counter > document.scan_queue_id.no_attempts:
                        self.pool.get('scan.document').write(cr, uid, document.id, {'task': (document.task or u"") + u'\nThe number of attempts to analyze the document has been exceeded.'})

        self.pool.get('scan.document').write(cr,uid,except_ids,{'state' : 'exception', 'except_state' : True},context)
        self.pool.get('scan.document').write(cr,uid,ids2,{'state' : 'analyzed', 'except_state' : False},context)
        self.writing_log(cr, uid, ids2, context)
        return res

    def writing_log(self, cr, uid, ids, context):

        for page in self.browse(cr, uid, ids, context):
            report = False
            if page.property_ids:
                for property in page.property_ids:
                    if property.value:
                        barcode = (property.value).split('/')
                        if barcode:
                            model = barcode[0]
                        if len(barcode) >=2 :
                            report = barcode[1]
                        if report and model:
                            report_ids = self.pool.get('ir.actions.report.xml').search(cr, uid, [('report_name','=', report)])
                            report_obj = self.pool.get('ir.actions.report.xml').browse(cr, uid, report_ids[0], context=context)
                            report_name = report_obj.report_name
                            cur = self.pool.get(model.split(',')[0]).search(cr, uid, [('id','=',int(model.split(',')[1]))])
                            if cur:
                                cur_obj = self.pool.get(model.split(',')[0]).browse(cr, uid, cur[0])
                                # import ipdb; ipdb.set_trace()
                                message = "The document " + report_name + " printed from the model " + model.split(',')[0] + " with id " + model.split(',')[1] + " has been parsed correctly. When processing will be attached to the expedient " + cur_obj.x_expedient_id.name + "."
                                self.pool.get('scan.document').log_expedient(cr, uid, page.id, message, False, cur_obj.x_expedient_id.id, context=context)
                        elif model:
                            cur = self.pool.get(model.split(',')[0]).search(cr, uid, [('id','=',int(model.split(',')[1]))])
                            if cur:
                                cur_obj = self.pool.get(model.split(',')[0]).browse(cr, uid, cur[0])
                                message = "The annex document, generated from the model " + model.split(',')[0] + " with id " + model.split(',')[1] + ", has been analyzed. When processing will be attached to the expedient " + cur_obj.x_expedient_id.name + "."
                                self.pool.get('scan.document').log_expedient(cr, uid, page.id, message, False, cur_obj.x_expedient_id.id, context=context)
                                
    
    def create_document(self, cr, uid, page, report, num_pags, model, current_obj, context=None):
        if context is None: context = {}
        report_ids = self.pool.get('ir.actions.report.xml').search(cr, uid, [('report_name','=', report)])
        report_obj = self.pool.get('ir.actions.report.xml').browse(cr, uid, report_ids[0], context=context)
        report_name = report_obj.report_name
        document_obj = self.pool.get('record.document')
        page_obj = self.pool.get('record.document.page')
        
        pages = not page.pdf_type and int(barcode[2].split("PAG")[1]) or 0
        document_ids = document_obj.search(cr, uid, [('report_id','=', report_obj.id),('model','=',model.split(',')[0]),('state','=','draft')])
        page_id = page_obj.create(cr, uid, {
                'name': _("Page %s of %s") % (str(pages),report_name),
                'page_number': pages,
                'scanned_document_id': page.id,
            })
        attachments = self.pool.get('ir.attachment').search(cr, uid, [('res_id','=', page.id),('res_model','=',page._name)])
        
        if not document_ids:
            document_id = document_obj.create(cr, uid, {
                'name': report_name,
                'required': pages and True or False,
                'required_pages': pages and pages or 1,
                'report_id': report_obj.id,
                'model': model,
                'pdf': (page.pdf_type and attachments) and attachments[0] or False,
               
            })
            document_obj.write(cr, uid, document_id,{'expedient_id': (document_obj.browse(cr, uid, document_id).model.x_expedient_id.id)})
        else:
            document_id = document_ids[0]
            
        page.write({'document_id': 'record.document,' + str(document_id)})

        if not page.pdf_type:
            attachment_id = self.pool.get('ir.attachment').create(cr, uid, {
                'res_id': page.id,
                'res_model': 'record.document.page',
                'name': report_name,
                'datas': page.data,
                'datas_fname': page.filename or page.name,
                'description': _('Document attached automatically'),
                'type2': report_name,
                'type': 'binary'

            }, context)
        else:
            attachment_id = attachments[0]
            self.pool.get('ir.attachment').write(cr, uid, [attachment_id], {'name': report_name, 'type2': report_name})
        page_obj.write(cr, uid, page_id, {'document_id': document_id,'attachment_id': attachment_id})
        cur_obj = self.pool.get(model.split(',')[0]).browse(cr, uid, int(model.split(',')[1]))
        message = "The document " + report_name + " printed from the model " + model.split(',')[0] + " with id " + model.split(',')[1] + " has been verified correctly. When processing is attached to the expedient " + cur_obj.x_expedient_id.name + "."
        self.pool.get('scan.document').log_expedient(cr, uid, page.id, message, False, cur_obj.x_expedient_id.id, context=context)
        
        return document_id
               
    def create_annex(self, cr, uid, page, model, context=None):
        at = []
        attachments = []

        obj = self.pool.get(model.split(',')[0]).browse(cr, uid, int(model.split(',')[1]))
        if 'x_expedient_id' in obj._columns:
            if obj.x_expedient_id:
                if obj.x_expedient_id.attachment_ids:
                    for attach in obj.x_expedient_id.attachment_ids:
                        at.append(attach.id)
                attachments = self.pool.get('ir.attachment').search(cr, uid, [('res_id','=', int(model.split(',')[1])),('res_model','=',model.split(',')[0])])
                if attachments:
                    for id in attachments:
                        cur = self.pool.get('ir.attachment').browse(cr, uid, id)
                        if cur.annex:
                            at.append(cur.id)
                            message = "The annex document " + cur.name + ", generated from the model " + model.split(',')[0] + " with id " + model.split(',')[1] + ", has been attached to the expedient " + obj.x_expedient_id.name + "."
                            self.pool.get('scan.document').log_expedient(cr, uid, page.id, message, False, obj.x_expedient_id.id, context=context)
                self.pool.get('expedient').write(cr, uid, [obj.x_expedient_id.id], {'attachment_ids': [(6,0,at)]})
                                
    def verified_document(self, cr, uid, ids, context=None):
        if not ids:
            ids = self.search(cr, uid, [('state','=','analyzed')])
        document_obj = self.pool.get('record.document')
        page_obj = self.pool.get('record.document.page')
        properties = False
        for page in self.browse(cr, uid, ids, context):
            document_id = False
            report = False
            model = False
            barcode = ''
            if page.property_ids:
                for property in page.property_ids:
                    if property.value:
                        barcode = property.value

            if barcode:
                barcode = barcode.split('/')
                model = barcode[0]
                cur = self.pool.get(model.split(',')[0]).search(cr, uid, [('id','=',int(model.split(',')[1]))])
                if cur:
                    if len(barcode) >=2:
                        report = barcode[1]
                    if report:
                        document_id = self.create_document(cr, uid, page, report, int(barcode[2].split("PAG")[1]), model, cur, context=context)
                    elif model and not report:
                        self.create_annex(cr, uid, page, model, context=context)
                else:
                    self.pool.get('scan.document').write(cr, uid, page.id, {'task': (page.task or "") + '\nThere is not %s model id %s' % (model.split(',')[0],model.split(',')[1])})

            if document_id and report:
                for document in document_obj.browse(cr, uid, [document_id], context=context):
                    if len(document.document_page_ids) == document.required_pages or not document.required:
                        if not document.pdf:
                            document.genereate_pdf()
                        else:
                            self.pool.get('ir.attachment').write(cr, uid, [document.pdf.id], {'res_id': document.model.id,
                                                                                            'res_model': document.model._name})
                            document.write({'state': 'done'})
                        if cur:
                            cur_obj = self.pool.get(model.split(',')[0]).browse(cr, uid, cur[0])
                            message = "He was created a new document for the model with the document record.document verified. You can access it from Menu > Document Management > Documents > Documents"
                            self.pool.get('record.document').log_expedient(cr, uid, document_id, message, False, cur_obj.x_expedient_id.id, context=context)


        return True

    def process_document(self, cr, uid, ids, context=None):
        if not ids:
            ids = self.search(cr, uid, [('state','=','verified')])

        res = super(scan_document, self).process_document(cr,
            uid, ids, context)
        expedient_document_id = False
        at = []
        continuate = False
        last = False
        ok = False
        document_ids = False
        report = False
        for page in self.browse(cr, uid, ids, context):
            barcode = ''
            if page.property_ids:
                for property in page.property_ids:
                    if property.value:
                        barcode = property.value
            at = []
            if barcode:
                barcode = barcode.split('/')
                model = barcode[0]
                if len(barcode) >=2 :
                    report = barcode[1]
                if report:
                    report_ids = self.pool.get('ir.actions.report.xml').search(cr, uid, [('report_name','=', report)])
                    report_obj = self.pool.get('ir.actions.report.xml').browse(cr, uid, report_ids[0], context=context)
                    if page.document_id:
                        document_ids = [page.document_id.id]
                    else:
                        document_ids = self.pool.get('record.document').search(cr, uid, [('report_id','=', report_obj.id),('model','=',model),('state','=','done')])
                if document_ids:
                    doc = self.pool.get('record.document').browse(cr, uid, document_ids[0], context=context)
                    if doc.model and doc.pdf:
                        attachment = doc.pdf
                        if 'x_expedient_id' in doc.model._columns:
                            obj = doc.model
                            if obj.x_expedient_id and obj.x_expedient_id.expedient_document:
                                for report in obj.x_expedient_id.expedient_document:
                                    if report.attach_mode and report.attach_mode == 'scanning' \
                                    and report.ir_act_report_xml_id and report.ir_act_report_xml_id.model \
                                    and report.ir_act_report_xml_id.model == (barcode[0]).split(',')[0] \
                                    and report.ir_act_report_xml_id.name == report_obj.name:
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
                                    if attach.res_model == (barcode[0]).split(',')[0]:
                                        if attach.name == report_obj.report_name:
                                            if last == False:
                                                at.append(attach.id)
                                        else:
                                            at.append(attach.id)
                                    else:
                                        at.append(attach.id)


                            self.pool.get('ir.attachment').write(cr, uid, [attachment.id], {'expedient_document_id': expedient_document_id})
                            
                            if attachment:
                                at.append(attachment.id)
                            if at:
                                self.pool.get('expedient').write(cr, uid, [obj.x_expedient_id.id], {'attachment_ids': [(6,0,at)]})
                                ok = True
                            at = []
                            message = "Document " + attachment.name + " has been processed and attached to expedient."
                            self.pool.get(obj._name).log_expedient(cr, uid, obj.id, message, False, obj.x_expedient_id.id, context=context)
        
        if ok == True:
            for page in self.browse(cr, uid, ids, context=context):
                self.write(cr, uid, [page.id],{'state': 'filed'})
                
        return res
        
    def verified(self, cr, uid, ids, context=None):
        if not ids:
            ids = self.search(cr, uid, [('state','=','analyzed')])
        workflow = netsvc.LocalService('workflow')
        for id in ids:
            workflow.trg_validate(uid, 'scan.document', id, 'verify_document', cr)

    def process(self, cr, uid, ids, context=None):
        if not ids:
            ids = self.search(cr, uid, ['|',('state','=','verified'),('state','=','processing')])

        workflow = netsvc.LocalService('workflow')
        for id in ids:
            workflow.trg_validate(uid, 'scan.document', id, 'process_document', cr)
        return True
    def analyze(self, cr, uid, ids, context=None):
        if not ids:
            ids = self.search(cr, uid, ['|',('state','=','pending'),('state','=','analyzing')])
        workflow = netsvc.LocalService('workflow')
        for id in ids:
            workflow.trg_validate(uid, 'scan.document', id, 'analyze_document', cr)
    def delete_crons(self, cr, uid, ids, context=None):
        
        if not ids:
            ids = self.pool.get('ir.cron').search(cr, uid, [('name','like','background'),('active','=',False)])
        if ids:
            self.pool.get('ir.cron').unlink(cr, uid, ids)
scan_document()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
