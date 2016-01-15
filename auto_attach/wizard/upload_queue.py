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


from osv import osv, fields

class upload_queue(osv.osv):
    '''
    Open ERP Model
    '''
    _name = 'scan.queue.upload.wizard'
    _description = 'upload Queue'

    _columns = {
        'queue_id': fields.many2one('scan.queue', 'Queue',
                domain=[('directory', '=', 1)], required=True)
    }

    def action_accept(self, cr, uid, ids, context):        
        queue_obj = self.pool.get('scan.queue')
        queues = []
        for queue in self.browse(cr, uid, ids, context):
            queues.append(queue.queue_id.id)

        queue_obj.upload_file_queue(cr, uid, queues, context)
        return {}

    def action_cancel(self, cr, uid, ids, context):
        return {}
upload_queue()

