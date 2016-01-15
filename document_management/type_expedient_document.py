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

class type_expedient_document(osv.osv):
    _name = "type.expedient.document"
    _description = "many2many between type of expedient and ir.actions.report.xml"
    _rec_name = "expedient_id"
    _order = "sequence asc"
    
    _columns = {
        'sequence': fields.integer("Sequence", required=True),
        'valid_last': fields.boolean('Valid the last'),
        'required': fields.boolean('Required'),
        'ir_act_report_xml_id': fields.many2one('ir.actions.report.xml', 'Document', required=True),
        'type_expedient_id': fields.many2one('type.expedient', 'Type of Expedient'),
        'half_page': fields.boolean('Printing half page'),
        'attach_mode': fields.selection([
            ('scanning', 'By Scanning'),
            ('printing', 'By printing'),
            ], 'Attach mode', required=True)
    }
    _defaults = {
        'attach_mode': 'printing'
    }
type_expedient_document()
