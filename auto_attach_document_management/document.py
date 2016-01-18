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
from openerp.osv import osv
from openerp.osv import fields
import base64
import tempfile
import os
import time
from tools.translate import _
import subprocess
class record_document(osv.osv):

    _name = 'record.document'
    _description = 'Document'
    _order = 'create_date desc'

    def _document_valid(self, cr, uid, ids, field_name, field_values,
            context=None):

        res = {}.fromkeys(ids, False)
        for doc in self.browse(cr, uid, ids, context):
            number = 0
            pages = set()
            for page in doc.document_page_ids:
                pages.add(page.page_number)
                number = len(pages)

            if number == doc.required_pages:
                res[doc.id] = True
        return res

    def _get_pages(self, cr, uid, ids, field_name, field_value, context=None):

        res = {}.fromkeys(ids, 0)
        for doc in self.browse(cr, uid, ids, context):
            pages = set()
            for page in doc.document_page_ids:
                pages.add(page.page_number)
                res[doc.id] = len(pages)
        return res

    def _get_states(self, cr, uid, context=None):
        return [('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancel')]

    # record_document_scanned
    def DocumentModel(self, cr, uid, context={}):
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

    state_only_read = {
        'draft': [('readonly', False), ],
    }

    _columns = {
        'name': fields.char('Name', size=128, required=True,
                readonly=True, states=state_only_read),
        'pages': fields.function(_get_pages, method=True, type='integer',
                string='Pages'),
        'required': fields.boolean('Required',  readonly=True,
                states=state_only_read),
        'required_pages': fields.integer('Required Pages', readonly=True,
                states=state_only_read),
        'valid': fields.function(_document_valid, method=True, type='boolean',
                string='Valid?', store=True),
        'document_page_ids': fields.one2many('record.document.page',
                'document_id', 'Document Pages',  readonly=True,
                states=state_only_read),
        'state': fields.selection(_get_states, 'State', readonly=True),
        'pdf': fields.many2one('ir.attachment', 'Pdf',  readonly=True,
                states=state_only_read),
        'report_id': fields.many2one('ir.actions.report.xml','Report', readonly=True),
        'model': fields.reference('Model',
                selection=DocumentModel, size=128, readonly=True),
        'date': fields.date('Date'),
        'expedient_id': fields.many2one('expedient', "Expedient", readonly=True)
    }
    
    def draft(self, cr, uid, ids, context=None):
        return

    def confirm(self, cr, uid, ids, context=None):
        return

    def cancel(self, cr, uid, ids, context=None):
        return

    def genereate_pdf(self, cr, uid, ids, context=None):
        if context is None: context = {}
        for doc in self.browse(cr, uid, ids, context):

            fp, pdffile_name = tempfile.mkstemp(suffix='.pdf')
            pages = []
            type = ''
            image_files = []
            for page in doc.document_page_ids:
                f, fname = tempfile.mkstemp()
                fpi = os.fdopen( f, 'wb+' )
                fpi.write(base64.decodestring(page.attachment_id.datas))
                image_files.append(fname)
                fpi.close()
                if not type:
                    type = page.attachment_id.type

            command = ['convert'] + image_files + [pdffile_name]
            process = subprocess.Popen(command, stdout=subprocess.PIPE)
            content = process.communicate()[0]
            fp = os.fdopen(fp, 'wb+')
            pdf_data = base64.encodestring(fp.read())
            fp.close()

            # Attach document to the appropiate reference
            attachment_id = self.pool.get('ir.attachment').create(cr, uid, {
                    'res_id': doc.id,
                    'res_model': 'record.document',
                    'name': doc.name,
                    'datas': pdf_data,
                    'datas_fname': doc.name + u".pdf",
                    'description': _('Pdf Generated from document Images'),
                    'type': type,
                    'type2':doc.report_id.report_name
                }, context)

            attachment_model = self.pool.get('ir.attachment').create(cr, uid, {
                    'res_id': doc.model.id,
                    'res_model': doc.model._name,
                    'name': doc.name,
                    'datas': pdf_data,
                    'datas_fname': doc.name + u".pdf",
                    'description': _('Pdf Generated from document Images'),
                    'type': type,
                    'type2':doc.report_id.report_name
                }, context)
                
            self.write(cr, uid, [doc.id], {'pdf': attachment_model,'state': 'done'}, context)
            type = ''
        return attachment_model

    _defaults = {
        'state': lambda *a: 'draft',
        'date': lambda *a:time.strftime('%Y-%m-%d'),
    }

record_document()


class record_document_page(osv.osv):
    _name = 'record.document.page'
    _description = 'Pages from Document'
    _order = 'sequence'

    _columns = {
        'name': fields.char('Name', size=128),
        'sequence': fields.integer('Sequence'),
        'page_number': fields.integer('Page Number'),
        'attachment_id': fields.many2one('ir.attachment', 'Attachment'),
        'document_id': fields.many2one('record.document', 'Document'),
        'scanned_document_id': fields.many2one('scan.document',
                'Scanned Document'),
        'state': fields.related('scanned_document_id', 'state', type='char', size=64, string='State')
    }

record_document_page()


class scan_queue(osv.osv):

    _inherit = 'scan.queue'
    _description = 'Scan Queue'

    _columns = {
        'last_document_id': fields.many2one('record.document',
                 'Last Document'),
    }

scan_queue()
