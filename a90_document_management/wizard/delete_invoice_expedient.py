# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos. All Rights Reserved
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

class delete_invoice_expedient(osv.osv_memory):

    _name = "delete.invoice.expedient"

    def action_delete_expedient(self, cr, uid, ids, context=None):
        context['manual_unlink'] = True
        for invoice in self.pool.get('account.invoice').browse(cr, uid, context['active_ids']):
            if invoice.x_expedient_id:
                self.pool.get('expedient').unlink(cr, uid, invoice.x_expedient_id.id, context=context)
                invoice.write({'x_expedient_id': False})

        return {}
