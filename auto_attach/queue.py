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

import os
import base64
import glob
import shutil

from osv import osv
from osv import fields


class scan_queue(osv.osv):

    _name = 'scan.queue'
    _description = 'Scan Queue'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'resolution': fields.integer('Resolution'),
        'directory': fields.boolean('Directory'),
        'file_directory': fields.char('File Directory', size=256, required=True, help="Directory where the files are up. For correct formatting path must end with /."),
        'processed_file_directory': fields.char('Processed File Directory',
                size=256, required=True, help="Directory where the processed files will OpenERP. For correct formatting path must end with /."),
        'ko_file_directory': fields.char('KO File Directory', size=256),
        'ir_sequence': fields.many2one( 'ir.sequence', 'Sequence', required=True)
    }

    def upload_file_queue(self, cr, uid, ids, context):

        for dir in self.browse(cr, uid, ids, context):
            files = []
            if dir.file_directory:
                for file in glob.glob(dir.file_directory + "/*.*"):
                    files.append(file)
            if files:
                files.sort()
                for file in files:
                    filename = file.split('/').pop()
                    content = base64.encodestring(open(file, 'r').read())
                    if self.create_page(cr, uid, dir.id, filename,
                            content, context):
                        dst_file = os.path.join(dir.processed_file_directory,
                                filename)
                        if os.path.exists(dst_file):
                            os.remove(dst_file)

                        shutil.move(os.path.join(dir.file_directory, filename),
                                dir.processed_file_directory)
                    else:
                        dst_file = os.path.join(dir.ko_file_directory,
                                filename)
                        if os.path.exists(dst_file):
                            os.remove(dst_file)

                        shutil.move(os.path.join(dir.file_directory, filename),
                                dir.ko_file_directory)
        return True

    def create_page(self, cr, uid, id, filename, content, context):

        page_obj = self.pool.get('scan.document')

        data = {
            'name': filename,
            'data': content,
            'filename': filename,
            'scan_queue_id': id
        }

        return page_obj.create(cr, uid, data, context)

scan_queue()

