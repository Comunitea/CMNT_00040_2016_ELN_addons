##############################################################################
#
# Copyright (c) 2012 NaN Projectes de Programari Lliure, S.L.
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



from openerp.osv import fields,osv
import base64

from NanScan.Template import *
from NanScan.Document import *
from NanScan.Recognizer import *
from NanScan.Ocr import *


class scan_document(osv.osv):

    _inherit = 'scan.document'

    def getRecognizers(self, cr, uid, ids, context):
        return ['dataMatrix']

    def analyze_document(self, cr, uid, ids, context=None):
        
        recognizer = Recognizer()
        recognizers = self.getRecognizers(cr, uid, ids, context)

        for document in self.browse(cr, uid, ids, context):
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

            boxes = recognizer.boxes('dataMatrix')
            self.process_datamatrix(cr, uid, document.id, boxes, context)

    def process_datamatrix(self, cr, uid, id, boxes, context):
        """
            @ids: scan.document analized
            @boxes: NaNScan Boxes class, with text and position...
        """
        for box in boxes:
            self.pool.get('scan.document.property').create(cr, uid, {
                        'name': 'dataMatrix',
                        'value': box.text,
                        'document_id': id,
                    }, context)
        

scan_document()


#    def process_document(self, cr, uid, ids, context=None):
#        self.process_page(cr, uid, ids, context )
#        self.write(cr, uid, ids, {'state': 'processed'}, context)
#
#    def process_barcode(self, cr, uid, barcode_ids, context ):
#        barcode_obj = self.pool.get('document.barcode')
#        record_type_obj = self.pool.get('record.type')
#        document_type_obj = self.pool.get('record.document.type')
#
#        record_type_ids = record_type_obj.search( cr, uid, [], context=context)
#        document_type_ids = document_type_obj.search( cr, uid, [],
#                context=context)
#
#        document_types = document_type_obj.browse(cr, uid, document_type_ids,
#                context=context )
#        record_types = record_type_obj.browse(cr, uid, record_type_ids,
#                 context=context)
#
#        rec_type=False
#        doc_type=False
#
#        for barcode in barcode_obj.browse(cr, uid, barcode_ids, context):
#            for document_type in document_types:
#                if doc_type:
#                    break
#                if document_type.barcode_identifier in barcode.barcode:
#                    doc_type = document_type.id
#                    break
#
#            for record_type in record_types:
#                if rec_type:
#                    break
#                if record_type.barcode_identifier in barcode.barcode:
#                    rec_type = record_type.id
#                    break
#
#        return (rec_type, doc_type)
#
#    def process_page(self, cr, uid, ids, context):
#
#        for page in self.browse(cr, uid, ids, context):
#            queue = page.scan_queue_id
#
#            if page.barcode_ids:
#                (type_id,record_id) = self.process_barcode(cr, uid,
#                    [x.id for x in page.barcode_ids], context)
#                document_id = self.pool.get('record.document').create(cr, uid, {
#                    'name': page.name,
#                    'type_id': type_id,
#                    'record_type_id':record_id,
#                    }, context)
#
#                self.write(cr, uid, [page.id], {'record_document_id':document_id},
#                        context)
#                self.pool.get('record.scan_queue').write(cr, uid,[queue.id],
#                    {'last_document_id':document_id}, context)
#            else:
#                 self.write(cr, uid, [page.id],
#                  {'record_document_id': queue.last_document_id.id}, context)
#
#record_document_line()
#

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

