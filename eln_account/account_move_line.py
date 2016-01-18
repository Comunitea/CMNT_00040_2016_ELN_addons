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

from openerp.osv import fields, osv, orm

class account_move_line(osv.osv):
    _inherit = "account.move.line"
    
    #Función pendiente de aplicar. Util en los pagos para ver numero de factura.
    #def name_get(self, cr, uid, ids, context=None):
    #    if not ids:
    #        return []
    #    result = []
    #    for line in self.browse(cr, uid, ids, context=context):
    #        if line.ref and line.invoice and line.invoice.number:
    #            result.append((line.id, (line.move_id.name or '')+' ['+line.invoice.number+']'+' ('+line.ref+')'))
    #        elif line.ref:
    #            result.append((line.id, (line.move_id.name or '')+' ('+line.ref+')'))
    #        elif line.invoice and line.invoice.number:
    #            result.append((line.id, (line.move_id.name or '')+' ['+line.invoice.number+']'))
    #        else:
    #            result.append((line.id, line.move_id.name))
    #    return result
    
account_move_line()
