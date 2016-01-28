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

from openerp.addons import jasper_reports



def parser( cr, uid, ids, data, context ):
    language = data['form']['language']
    delivery_address = data['form']['delivery_address']
    signed = data['form']['signed']
    parameters = {}
    ids = ids
    name = 'report.purchase_order'
    model = 'purchase.order'
    data_source = 'model'
    parameters['lang'] = language
    print language
    parameters['delivery_address'] = delivery_address
    parameters['signed'] = signed
    return { 
        'ids': ids, 
        'name': name, 
        'model': model, 
        'records': [], 
        'data_source': data_source,
        'parameters': parameters,
    }
jasper_reports.report_jasper('report.purchase_order', 'purchase.order', parser)
