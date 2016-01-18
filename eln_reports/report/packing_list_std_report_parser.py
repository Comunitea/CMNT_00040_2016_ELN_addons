# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
import pooler
import jasper_reports
from datetime import datetime
from openerp.tools.translate import _

def parser( cr, uid, ids, data, context ):
    parameters = {}
    ids = ids
    name = 'report.packing_list_std'
    model = 'stock.picking'
    data_source = 'model'
    
    cliente = pooler.get_pool(cr.dbname).get('stock.picking').read(cr,uid,ids)
    #import ipdb; ipdb.set_trace()
    cliente = pooler.get_pool(cr.dbname).get('res.partner.address').read(cr,uid,cliente[0]['address_id'][0])
    cliente = pooler.get_pool(cr.dbname).get('res.partner').read(cr,uid,cliente['partner_id'][0])
    language = cliente['lang']
    #parameters['lang'] = language
    context['lang'] = language

    return { 
        'ids': ids, 
        'name': name, 
        'model': model, 
        'records': [], 
        'data_source': data_source,
        'parameters': parameters,
    }
jasper_reports.report_jasper( 'report.packing_list_std', 'stock.picking', parser )
