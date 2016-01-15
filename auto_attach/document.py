##############################################################################
#
# Copyright (c) 2007-2012 NaN Projectes de Programari Lliure, S.L.
#                         All Rights Reserved.
#                         http://www.NaN-tic.com
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################


import re
import base64
import datetime
import time

import netsvc
from osv import osv
from osv import fields
from tools.translate import _

from NanScan.Template import *
from NanScan.Document import *
from NanScan.Recognizer import *
from NanScan.Ocr import *


class scan_document(osv.osv):

    _name = 'scan.document'
    _order = 'upload_date desc,sequence'

    state_only_read = {
        'pending': [('readonly', False), ],
        'analyzed': [('readonly', False), ],
    }

    # record_document_scanned
    def attachableDocuments(self, cr, uid, context={}):
        ids = self.pool.get('ir.model').search(cr, uid, [], context=context)
        records = self.pool.get('ir.model').read(cr, uid, ids,
                    ['model', 'name'], context)
        data = []
        for record in records:
            model = record['model']
            name = record['name']
            if len(name) > 30:
                name = name[:30] + '...'
            data.append((model, name))
        return data

    _columns = {
        'name': fields.char('Name', 64, readonly=True, states=state_only_read),
        'sequence': fields.char('Sequence', size=256) ,
        'data': fields.binary('Data'),
        'filename': fields.char('Filename', 80, readonly=True,
                states=state_only_read),
        'property_ids': fields.one2many('scan.document.property', 'document_id',
                'Properties', readonly=True, states=state_only_read),
        'template_id': fields.many2one('scan.template', 'Template',
                readonly=True, states=state_only_read),
        'scan_queue_id': fields.many2one('scan.queue', 'Scan Queue',
                required=True),
        'document_id': fields.reference('Document',
                selection=attachableDocuments, size=128, readonly=True,
                states=state_only_read),
        'attachment_id': fields.many2one('ir.attachment', 'Attachment',
                readonly=True, ondelete='cascade',
                help='Attachment created by this document.'),
        'task' : fields.text('Task', readonly=True),
        'upload_date': fields.datetime('Upload date', readonly=True),
        'state': fields.selection( [
            ('pending', 'Pending'), ('analyzing', 'Analyzing'),
            ('analyzed', 'Analyzed'), ('verified', 'Verified'),
            ('processing', 'Processing'), ('processed', 'Processed')],
            'State', required=True, readonly=True )
    }
    _defaults = {
        'state': lambda *a: 'pending',
        'upload_date': lambda *a: time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # record_document_scanned
    def image_from_pdf(self, pdf):
        """
        Extracts and returns the first image found in a PDF file.

        This should not be necessary in the future as ideally NanScan should
        be able to handle PDF files, and in general, multi-page documents.
        """
        startmark = "\xff\xd8"
        startfix = 0
        endmark = "\xff\xd9"
        endfix = 2
        i = 0

        image = False
        njpg = 0
        while True:
            istream = pdf.find("stream", i)
            if istream < 0:
                break
            istart = pdf.find(startmark, istream, istream + 20)
            if istart < 0:
                i = istream + 20
                continue
            iend = pdf.find("endstream", istart)
            if iend < 0:
                raise Exception("Didn't find end of stream!")
            iend = pdf.find(endmark, iend - 20)
            if iend < 0:
                raise Exception("Didn't find end of JPG!")

            istart += startfix
            iend += endfix
            image = pdf[istart:iend]

            njpg += 1
            i = iend
            break
        return image

    # record_document_scanned
    def create(self, cr, uid, values, context=None):
        # If file is a PDF try to extract its JPEG.
        datas = values.get('datas')
        if datas:
            datas = base64.decodestring(datas)
            if datas.lower().startswith('%pdf'):
                data = self.image_from_pdf(datas) 
                if data:
                    values['datas'] = base64.encodestring(data)
                else:
                    values['datas'] = False
                filename = values.get('filename')
                if filename:
                    # Set .jpg extension
                    if '.' in filename:
                        filename = filename.rpartition('.')[0]
                    values['filename'] = '%s.jpg' % filename

        obj_seq = self.pool.get('ir.sequence')
        queue_id = values.get('scan_queue_id')
        queue = self.pool.get('scan.queue').browse(cr, uid, queue_id, context)
        number = obj_seq.get_id(cr, uid, queue.ir_sequence.id,
                    context=context)
        values['sequence'] = number
        return super(scan_document, self).create(cr, uid, values, context)

    # scan_document
    def write(self, cr, uid, ids, values, context=None):
        # Analyze after writting as it will modify the objects and thus a 
        #"modified in the meanwhile" would be thrown, so by now check which 
        # of the records we'll want to analyze later
        toAnalyze = []
        if 'template_id' in values:
            for x in self.read(cr, uid, ids, ['state', 'template_id'], context):
                # We only analyze the document if template has changed and the
                # document is in 'analyzed' state.
                if x['state'] == 'analyzed' and \
                     x['template_id'] != values['template_id']:
                    toAnalyze.append({'id': x['id'],
                                        'template_id': values['template_id']
                                       })

        # If file is a PDF try to extract its JPEG.
        datas = values.get('datas')
        if datas:
            datas = base64.decodestring(datas)
            if datas.lower().startswith('%pdf'):
                data = self.image_from_pdf( datas ) 
                if data:
                    values['datas'] = base64.encodestring(data)
                else:
                    values['datas'] = False
                filename = values.get('filename')
                if filename:
                    # Set .jpg extension
                    if '.' in filename:
                        filename = filename.rpartition('.')[0]
                    values['filename'] = '%s.jpg' % filename 

        ret = super(scan_document, self).write(cr, uid, ids, values, context)

        for x in toAnalyze:
            self.analyzeDocumentWithTemplate(cr, uid, x['id'],
                x['template_id'], context)
        return ret

    # scan_document
    def analyze_document_background(self, cr, uid, imageIds, context=None):
        # Use ir.cron to execute job in the background. We do not use threading
        # because in case of the server crashing while the process is being
        # executed it would not be recovered.
#
        # Also, we need to set nextcall in some time in the future, otherwise
        # it's executed within this transaction, meaning trg_validate() can not
        # work correctly because current state has not yet changed to
        # 'analyzing'.

        nextcall = datetime.datetime.now() + datetime.timedelta(seconds=5)
        self.pool.get('ir.cron').create(cr, uid, {
            'name': 'Analyze document background',
            'user_id': uid,
            'model': 'scan.document',
            'function': 'analyze_document_analyzing_to_analyzed',
            'args': repr([imageIds, True]),
            'nextcall': nextcall.strftime('%Y-%m-%d %H:%M:%S'),
            'active': True
        }, context)

    # scan_document
    def analyze_document_analyzing_to_analyzed(self, cr, uid, imageIds, 
            context=None):

        workflow = netsvc.LocalService('workflow')
        for id in imageIds:
            workflow.trg_validate(uid, 'scan.document', id,
                    'analyzing_to_analyzed', cr)

    # scan_document
    def analyze_documents_batch(self, cr, uid, imageIds, context=None):
        self.analyze_document(cr, uid, imageIds, context=context)
        self.pool.get('res.request').create(cr, uid, {
            'act_from': uid,
            'act_to': uid,
            'name': 'Finished analyzing documents',
            'body': 'The auto_attach system has finished analyzing the '
                    'documents you requested. You can now go to the Analyzed'
                    ' Documents queue to verify and process them.',
        }, context)

    # scan_document
    def analyze_document(self, cr, uid, imageIds, context=None):
        # Load templates into 'templates' list

        scan_template_proxy = self.pool.get('scan.template')
        templates = scan_template_proxy.getAllTemplates(cr, uid, context)

        templatesWithAnalysis = [x for x in templates if x.analysisFunction]
        templatesWithoutAnalysis = [x for x in templates if not \
                 x.analysisFunction]

        # Search what recognizers are used so we do not execute unnecessary 
        # processes.
        recognizers = set()
        for template in templates:
            for box in template.boxes:
                recognizers.add(box.recognizer)
        recognizers = list(recognizers)

        recognizer = Recognizer()

        # Iterate over all images and try to find the most similar template
        for document in self.browse(cr, uid, imageIds, context):
            if document.state not in ('pending', 'analyzing'):
                continue
            if not document.data:
                continue
            fp, image = tempfile.mkstemp()
            fp = os.fdopen(fp, 'wb+')
            try:
                fp.write(base64.decodestring(document.data))
            finally:
                fp.close()
            recognizer.recognize(QImage(image), recognizers)

            template = False
            doc = False
            for template in templatesWithAnalysis:
                function = re.sub(' *', '', template.analysisFunction)
                if function.endswith('()'):
                    function = function[:-2]
                doc = eval('''self.%s(cr, uid, document, template, 
                    recognizer, context)''' % function)
                if doc:
                    break

            if not doc:
                result = recognizer.findMatchingTemplateByOffset(
                        templatesWithoutAnalysis)
                template = result['template']
                doc = result['document']

            if not template:
                print "No template found for document %s." % document.name
            else:
                print "The best template found for document %s is %s." % (
                        document.name, template.name)

            if template:
                template_id = template.id
            else:
                template_id = False
            self.write(cr, uid, [document.id], {
                'template_id': template_id, 
                'state': 'analyzed'
            }, context=context)
            if doc:
                for box in doc.boxes:
                    self.pool.get('record.document.property').create(cr, uid, {
                        'name': box.name, 
                        'value': box.text, 
                        'document_id': document.id,
                        'template_box_id': box.templateBox and \
                                box.templateBox.id or False
                    }, context)

            if document.state == 'analyzing':
                self.pool.get('res.request').create(cr, uid, {
                    'act_from': uid,
                    'act_to': uid,
                    'name': 'Finished analyzing document',
                    'body': 'The auto_attach system has finished analyzing '
                            'the document you requested. A reference to the'
                            ' document can be found in field Document Ref 1.',
                    'ref_doc1': 'scan.document,%s' % document.id,
                }, context)

        self.executeAttachs(cr, uid, imageIds, context)
        self.executeActions(cr, uid, imageIds, True, context)

    def analyzeDocumentWithTemplate(self, cr, uid, documentId, templateId,
             context):

        # Whether templateId is valid or not
        # Remove previous properties
        ids = self.pool.get('scan.document.property').search(cr, uid,
                [('document_id', '=', documentId)], context=context)
        self.pool.get('scan.document.property').unlink(cr, uid, ids, context)

        if templateId:
            template = self.pool.get('scan.template').getTemplateFromId(cr,
                uid, templateId, context)

            documents = self.read(cr, uid, [documentId], context=context)
            if not documents:
                return
            document = documents[0]

            fp, image = tempfile.mkstemp()
            fp = os.fdopen(fp, 'wb+')
            try:
                fp.write(base64.decodestring(document['datas']))
            finally:
                fp.close()

            recognizer = Recognizer()
            recognizer.recognize(QImage(image))
            doc = recognizer.extractWithTemplate(image, template)

            obj = self.pool.get('scan.document')
            for box in doc.boxes:
                obj.create(cr, uid, {
                    'name': box.templateBox.name,
                    'value': box.text, 
                    'document_id': document['id'],
                    'template_box_id': box.templateBox.id
                }, context)
        self.executeAttachs(cr, uid, [documentId], context)
        self.executeActions(cr, uid, [documentId], True, context)

    def process_document_background(self, cr, uid, imageIds, context=None):
        # Use ir.cron to execute job in the background. We do not use threading
        # because in case of the server crashing while the process is being 
        # executed it would not be recovered.
        #
        # Also, we need to set nextcall in some time in the future, otherwise 
        # it's executed within this transaction, meaning trg_validate() can 
        # not work correctly because current state has not yet changed 
        # to 'analyzing'.

        nextcall = datetime.datetime.now() + datetime.timedelta(seconds=5)
        self.pool.get('ir.cron').create(cr, uid, {
            'name': 'Process document background',
            'user_id': uid,
            'model': 'scan.document',
            'function': 'process_document_processing_to_processed',
            'args': repr([imageIds, True]),
            'nextcall': nextcall.strftime('%Y-%m-%d %H:%M:%S'),
            'active': True
        }, context)

    def process_document_processing_to_processed(self, cr, uid, imageIds, 
            context=None):

        workflow = netsvc.LocalService('workflow')
        for id in imageIds:
            workflow.trg_validate(uid, 'scan.document', id,
                        'processing_to_processed', cr)

    def process_document(self, cr, uid, ids, context=None):
        self.executeActions(cr, uid, ids, False, context)

    def _parseFunction(self, function, properties):
        expression = re.match('(.*)\((.*)\)', function)
        name = expression.group(1)
        parameters = expression.group(2)
        if name not in dir(self):
            print "Function '%s' not found" % (name)
            return False

        parameters = parameters.split(',')
        newParameters = []
        for p in parameters:
            value = p.strip()
            if value.startswith('#'):
                if value[1:] not in properties:
                    print "Property '%s' not found" % value
                    newParameters.append("''")
                    continue
                value = properties[value[1:]]
            value = "'" + value.replace("'","\\'") + "'"
            if type(value) != unicode:
                value = unicode(value, errors='ignore')
            newParameters.append(value)
        return (name, newParameters)

    def executeActions(self, cr, uid, ids, explain, context):
        if context is None:
            # As workflows do not support context, we create, at least the lang
            # entry so translations work as expected when calling action 
            # functions.
            user = self.pool.get('res.users').browse(cr, uid, uid, context)
            context = {
                'lang': user.context_lang
            }

        for document in self.browse(cr, uid, ids, context):
            if not explain and document.state not in ('verified', 'processing'):
                continue

            if not explain and document.document_id:
                # Attach document to the appropiate reference
                ref = document.document_id.split(',')
                model = ref[0]
                id = ref[1]

                # Ensure attachment name is not duplicated because there's a 
                # restriction in ir.attachment model.
                count = 0
                while True:
                    current_name = '%s (%d)' % (document.name, count)
                    name = count and current_name or document.name
                    ids = self.pool.get('ir.attachment').search(cr, uid, [
                        ('res_id','=',id),
                        ('res_model','=',model),
                        ('name','=',name)
                    ], context=context)
                    if not ids:
                        break
                    count += 1

                attachment_id = self.pool.get('ir.attachment').create( cr, uid,
                    { 
                    'res_id': id,
                    'res_model': model,
                    'name': name,
                    'datas': document.data,
                    'datas_fname': document.filename or document.name,
                    'description': _('Document attached automatically'),
                }, context)
                self.write(cr, uid, [document.id], {
                    'state': 'processed',
                    'attachment_id': attachment_id,
                }, context)

            task = None
            if document.template_id:
                function = document.template_id.action_function
                if function:
                    properties = dict([(x.name, unicode(x.value)) \
                            for x in document.property_ids])
                    (name, parameters) = self._parseFunction(function, 
                                            properties)
                    task = eval("""obj.%s(cr, uid, document.id, explain,
                         %s, context)""" % (name, ','.join(parameters)))
            if explain:
                self.write(cr, uid, [document.id], {'task': (document.task or "") + task})

    def executeAttachs(self, cr, uid, ids, context=None):
        if context is None:
            # As workflows do not support context, we create, at least the lang
            # entry so translations work as expected when calling action 
            # functions.
            user = self.pool.get('res.users').browse(cr, uid, uid, context)
            context = {
                'lang': user.context_lang
            }

        for document in self.browse(cr, uid, ids, context):
            reference = None
            if document.template_id:
                function = document.template_id.attach_function
                if function:
                    properties = dict([(x.name, x.value) \
                                        for x in document.property_ids])

                    (name, parameters) = self._parseFunction(function,
                                                properties)
                    reference = eval("""obj.%s(cr, uid, document.id, 
                        %s, context)""" % (name, u','.join(parameters)))

            if reference:
                self.write(cr, uid, [document.id], {
                    'document_id': '%s,%s' % (reference[0], reference[1])
                }, context)
            else:
                self.write(cr, uid, [document.id], {
                    'document_id': False
                }, context)

    def actionAddPartner(self, cr, uid, document_id, explain, name, context):
        """
        This is sample function to be used as action function in a template.
        """

        if explain:
            return _("""A new partner with name '%s' will be created 
                (if it doesn't exist already).""") % name

        if not self.pool.get('res.partner').search(cr, uid,
                [('name', '=', name)], context=context):
            self.pool.get('res.partner').create(cr, uid, {
                'name': name
            }, context)
        return True

    def attachModelByField(self, cr, uid, document_id, model, field,
            name, context):
        """
        This is sample function to be used as an attach function in a template.
        """

        ids = self.pool.get(model).search(cr, uid, [(field, '=', name)],
                context=context)
        if not ids:
            return False
        return (model, ids[0])

scan_document()


class scan_document_property(osv.osv):

    _name = 'scan.document.property'
    _columns = {
        'name': fields.char('Text', 256),
        'value': fields.char('Value', 256),
        'document_id': fields.many2one('scan.document', 'Document', 
            required=True, ondelete='cascade'),
        'template_box_id': fields.many2one('scan.template.box', 'Template Box',
            ondelete='set null')
    }
scan_document_property()















