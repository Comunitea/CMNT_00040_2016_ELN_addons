# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import base64
from osv import osv, fields
from openerp.addons.document import nodes

class document_file(osv.osv):
    _inherit = 'ir.attachment'
    """Sobreescribimos función original para añadir la linea:
        fbro.user_id = None en _data_get
        En principio es para solucionar un problema que se da al intentar acceder a un
        documento guardado por un usuario cualquiera. Al acceder al documento con otro usuario,
        si el usuario que está como propietario se encuentra en otra compañia en ese momento
        da un error de permisos porque no usa el usuario activo.
        el _data_set lo ponemos porque está en el campo función.
    """

    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        fbrl = self.browse(cr, uid, ids, context=context)
        nctx = nodes.get_node_context(cr, uid, context={})
        # nctx will /not/ inherit the caller's context. Most of
        # it would be useless, anyway (like active_id, active_model,
        # bin_size etc.)
        result = {}
        bin_size = context.get('bin_size', False)

        for fbro in fbrl:
            fbro.user_id = None
            fnode = nodes.node_file(None, None, nctx, fbro)
            if not bin_size:
                    data = fnode.get_data(cr, fbro)
                    result[fbro.id] = base64.encodestring(data or '')
            else:
                    result[fbro.id] = fnode.get_data_len(cr, fbro)

        return result
    
    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        if not value:
            return True
        fbro = self.browse(cr, uid, id, context=context)
        nctx = nodes.get_node_context(cr, uid, context={})
        fnode = nodes.node_file(None, None, nctx, fbro)
        res = fnode.set_data(cr, base64.decodestring(value), fbro)
        return res

    _columns = {
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='File Content', type="binary", nodrop=True),
    }

document_file()
