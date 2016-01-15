##############################################################################
#
# Copyright (c) 2007-2009 Albert Cervera i Areny <albert@nan-tic.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from osv import osv, fields
import netsvc

class analyze_document_queue_wizard(osv.osv_memory):
    _name = 'analyze.document.queue.wizard'
    _columns = {
        'documents': fields.text('Documents', readonly=True),
        'background': fields.boolean('Execute in the background')
    }
    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """
        res = {}
        values = []
        if not context:
            context = {}
        if context.get('active_model', False) and context['active_model'] == 'scan.document':
            ids = context.get('active_ids', False)
        else:
            ids = self.pool.get('scan.document').search(cr, uid, [('state','=','pending')], context=context)
            values = self.pool.get('scan.document').read(cr, uid, ids, ['name'], context=context)
        if 'documents' in fields:
            res.update({'documents':'\n'.join([x['name'] for x in values])})
        if 'background' in fields:
            res.update({'background': True})
        return res

  
    def act_analyze(self, cr, uid, ids, context):
        # import ipdb; ipdb.set_trace()
        if context is None: context = {}
        ids_doc = []
        if context.get('active_model', False) and context['active_model'] == 'scan.document':
            if context.get('active_ids', False):
                ids_doc = context['active_ids']
        else:
            ids_doc = self.pool.get('scan.document').search(cr, uid,
                    [('state', '=', 'pending')], context=context)

        form_obj = self.browse(cr, uid, ids)[0]
        if form_obj.background:
            signal = 'pending_to_analyzing'
        else:
            signal = 'analyze_document'
        workflow = netsvc.LocalService('workflow')
        for id in ids_doc:
            workflow.trg_validate(uid, 'scan.document', id, signal, cr)

        return {}

    
analyze_document_queue_wizard()
