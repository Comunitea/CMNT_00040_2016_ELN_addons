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
from osv import osv, fields

class ir_attachment(osv.osv):
    _inherit = "ir.attachment"
    def _get_sequence(self, cr, uid, ids, context=None):
        result = []
        for line in self.pool.get('expedient.document').browse(cr, uid, ids, context=context):
            ids_attach = self.pool.get('ir.attachment').search(cr, uid, [('expedient_document_id','=',line.id)])
            result.extend(ids_attach)
        return result
    _columns = {
        'expedient_id': fields.many2one('expedient', 'expedient'),
        'type2': fields.char('Type', size=148, readonly=True),
        'expedient_document_id': fields.many2one('expedient.document', 'Document', readonly=True),
        'seq_id': fields.related('expedient_document_id', 'sequence', type="integer", readonly=True, string="Sequence",
            store = {
                'ir.attachment': (lambda self, cr, uid, ids, c={}: ids, ['expedient_document_id'], 10),
                'expedient.document': (_get_sequence, None, 10),
            })
    }
    _defaults = {
        'seq_id':0
    }
    _order = "seq_id asc"
    
ir_attachment()