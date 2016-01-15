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

from openerp import tools
from openerp.osv import osv, fields

class expedient_analysis(osv.osv):
    _name = "expedient.analysis"
    _description = "Analysis of expedient documents"
    _auto = False
    _rec_name = 'expedient'
    _columns = {
        'id' : fields.integer('Type document',readonly=True),
        'expedient': fields.many2one('expedient', 'Expedient',readonly=True),
        'parent_expedient': fields.many2one('expedient', 'Parent expedient',readonly=True),
        'partner': fields.char('Partner', size=255,readonly=True),
        'date_origin':fields.char('Date', size=255,readonly=True),
        'origin': fields.char('Origin', size=255,readonly=True),
        'type' : fields.many2one('type.expedient','Type', readonly=True),
        'group' : fields.char('Group', size=255, readonly=True),
        'state_expedient' : fields.selection([
            ('created', 'Created'),
            ('incomplete', 'Incomplete'),
            ('completed', 'Completed'),
            ('printed', 'Printed'),
            ('finalized', 'Finalized')], 'State expedient', readonly=True),
        'model_name' : fields.many2one('ir.actions.report.xml','Type name document', readonly=True),
        'state_document': fields.selection([
            ('valid', 'Valid'),
            ('not_valid','Not Valid')],'State document',readonly=True),
        'annex': fields.selection([
            ('ok','Ok'),
            ('false', 'False'),
            ('not_necessary','Not necessary')], 'Annex',readonly=True)
        
        
        
        
    }
    _order = 'expedient desc'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'expedient_analysis')
        cr.execute("""
            create or replace view expedient_analysis as (
            select ex.id ,
            e.id as expedient,
            case when e.parent_expedient is null then e.id else e.parent_expedient end as parent_expedient,
            e.partner_name_expedient as partner,
            e.date_origin_model as date_origin,
            e.name_origin_model as origin,
            t.id as type,
            e.wzd_name as group ,
            e.state as state_expedient,
            xm.id as model_name,

            case when (xm.report_name in
            (select ir.type2 from ir_attachment ir
            where ir.expedient_id = e.id) and ex.required = true) or ex.required = false
            then 'valid' else 'not_valid' end as state_document,

            case when((select stock.attached from stock_picking stock
            where stock.x_expedient_id = e.id) = true )then (case when
            (select ir.annex from ir_attachment ir where ir.expedient_id = e.id) = true
            then 'ok' else 'false' end) else 'not_necessary' end as annex


            from expedient_document ex
                inner join expedient e on e.id = ex.expedient_id
                inner join type_expedient t on (e.type = t.id)
                inner join ir_act_report_xml xm on (xm.id = ex.ir_act_report_xml_id)
                
            ) 
        """)
