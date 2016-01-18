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
from openerp.osv import osv, fields
from pyPdf import PdfFileReader, PdfFileWriter
import os
import base64
import glob
import shutil
from openerp.tools.translate import _
import subprocess


class scan_queue(osv.osv):

    _inherit = 'scan.queue'
    _columns = {
        'no_attempts': fields.integer('No attempts', help="Number of times to try to analyze a document. When exceeded, the state will 'exception'.")
    }

    def queue_upload(self,cr, uid, ids, context=None):
        queues = self.pool.get('scan.queue').search(cr, uid, [])
        list_queue = []
        for queue in queues:
            obj = self.pool.get('scan.queue').browse(cr, uid, queue)
            list_queue.append(obj.id)
        if list_queue:
            self.pool.get('scan.queue').upload_file_queue(cr, uid, list_queue, context)

    def upload_file_queue(self, cr, uid, ids, context=None):

        for dir in self.browse(cr, uid, ids, context):
            if dir.file_directory:
                for file in glob.glob(dir.file_directory + "/*.*"):
                    extension = file.split('/')[-1].split('.')[-1]
                    if extension == "pdf":
                        filename = file.split('/').pop()
                        filename2 = filename.split('.pdf')[0]
                        output_filename = filename2 + u'1p.png'
                        output_path = os.path.join(dir.file_directory,output_filename)
                        input_path = os.path.join(dir.file_directory,filename)
                        cmd = u'pdfdraw -o ' + output_path + u" " + input_path + u' 0'
                        a = subprocess.call(cmd, shell=True)
                        
                        content = base64.encodestring(open(output_path, 'r').read())
                        create_page = self.create_page(cr, uid, dir.id, output_filename,
                                content, context)
                        if create_page:
                            
                            dst_file = os.path.join(dir.processed_file_directory,
                                    output_filename)
                            if os.path.exists(dst_file):
                                os.remove(dst_file)

                            shutil.move(output_path,
                                    dir.processed_file_directory)
                                    
                            self.pool.get('scan.document').write(cr, uid, [create_page], {'pdf_type': True})
                                    
                            attachment_id = self.pool.get('ir.attachment').create(cr, uid, {
                                'res_id': create_page,
                                'res_model': 'scan.document',
                                'name': filename,
                                'datas': base64.encodestring(open(input_path, 'r').read()),
                                'datas_fname': filename,
                                'description': _('Pdf file'),
                                'type': 'binary'
    
                            }, context)
                            
                            dst_file = os.path.join(dir.processed_file_directory,
                                    filename)
                            if os.path.exists(dst_file):
                                os.remove(dst_file)
                                
                            shutil.move(os.path.join(input_path),
                                    dir.processed_file_directory)
                        else:
                            dst_file = os.path.join(dir.ko_file_directory,
                                   output_filename)
                            if os.path.exists(dst_file):
                                os.remove(dst_file)

                            shutil.move(output_path,
                                    dir.ko_file_directory)

        super(scan_queue, self).upload_file_queue(cr, uid, ids, context)
        return True


scan_queue()


