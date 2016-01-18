# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
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
from openerp import netsvc

class verify_document_queue_wizard(osv.osv_memory):
    _name = 'verify.document.queue.wizard'
    _columns = {
        'documents': fields.text('Documents', readonly=True),
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
            ids = self.pool.get('scan.document').search(cr, uid, [('state','=','analyzed')], context=context)
            values = self.pool.get('scan.document').read(cr, uid, ids, ['name'], context=context)
        if 'documents' in fields:
            res.update({'documents':'\n'.join([x['name'] for x in values])})
        return res

    def act_process(self, cr, uid, ids, context):
        if context is None: context = {}
        ids_doc = []
        if context.get('active_model', False) and context['active_model'] == 'scan.document':
            if context.get('active_ids', False):
                ids_doc = context['active_ids']
        else:
            ids_doc = self.pool.get('scan.document').search(cr, uid, [('state','=','analyzed')], context=context)
        form_obj = self.browse(cr, uid, ids)[0]
        signal = 'verify_document'
        workflow = netsvc.LocalService('workflow')
        for id in ids_doc:
            workflow.trg_validate(uid, 'scan.document', id, signal, cr)

        return {}

   
verify_document_queue_wizard()
