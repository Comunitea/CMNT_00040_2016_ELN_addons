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
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv, fields

class ir_model_expedient(osv.osv):
    _name = 'ir.model.expedient'
    _description = 'many2many between expedient and ir.model'
    _rec_name = "expedient_id"
    _columns = {
        'ir_model': fields.many2one('ir.model', 'Model', required=True),
        'cancellation': fields.char("Cancellation", size=255,help="State in which this model should be canceled. Example: For the sales model in the state set aside would be canceled: cancel"),
        'expedient_id': fields.many2one('expedient', 'Expedient', readonly=True),
    }
ir_model_expedient()

