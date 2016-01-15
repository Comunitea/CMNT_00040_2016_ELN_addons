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
from osv import osv, fields

class budget_line(osv.osv):
    _inherit = 'budget.line'
    _columns = {
        'jan_amount': fields.float('January'),
        'feb_amount': fields.float('February'),
        'mar_amount': fields.float('March'),
        'apr_amount': fields.float('April'),
        'may_amount': fields.float('May'),
        'jun_amount': fields.float('June'),
        'jul_amount': fields.float('July'),
        'aug_amount': fields.float('August'),
        'sep_amount': fields.float('September'),
        'oct_amount': fields.float('October'),
        'nov_amount': fields.float('November'),
        'dec_amount': fields.float('December')
    }
budget_line()