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

from openerp.osv import fields, osv
from openerp import netsvc
from openerp.tools.translate import _
import time
import logging

_logger = logging.getLogger(__name__)

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def action_reopen(self, cr, uid, ids, context=None):
        """ Changes picking and move state from done to confirmed/assigned.
        @return: True
        """
        move_line_obj = self.pool.get('stock.move')

        for pick in self.browse(cr, uid, ids):
            _logger.debug('Action reopen pick %s ' %(pick.name))
            ml_ids = []
            for ml in pick.move_lines:
                if ml.state != 'cancel':
                    ml_ids.append(ml.id)
            _logger.debug('Action reopen move %s ' %(ml_ids))
            move_line_obj.write(cr, uid, ml_ids, {'state': 'draft'})

            self.write(cr, uid, pick.id, {'state': 'draft'})
            wf_service = netsvc.LocalService("workflow")

            wf_service.trg_delete(uid, 'stock.picking', pick.id, cr)
            wf_service.trg_create(uid, 'stock.picking', pick.id, cr)
            
            #Ponemos el albarán en confirmado y asignamos disponibilidad (forzamos ya que se supone que se procesó habiendo disponibilidad). 
            #Al ponerlos en corfirmado evitamos poder eliminar lineas y además al forzar disponibilidad conservamos la disponibildad que tenía.
            #Si queremos que se quede en borrador debemos quitar las dos lineas de abajo
            wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_confirm', cr)
            #self.action_assign(cr, uid, [pick.id])
            self.force_assign(cr, uid, [pick.id])

            self.log_picking(cr, uid, ids, context=context)  

        return True

stock_picking()
