# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2017 QUIVAL, S.A. All Rights Reserved
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
from openerp import models, api, _
from openerp.exceptions import except_orm


class DesadvParser(models.AbstractModel):
    _name = 'report.eln_edi.desadv_report'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report_name = 'eln_edi.desadv_report'
        if not data:
            raise except_orm(_('Error'),
                             _('You must print it from a wizard'))
        line_objs = {}
        for picking_id in data['lines_dic']:
            picking = self.env['stock.picking'].browse(int(picking_id))
            line_objs[picking] = data['lines_dic'][picking_id]

        docargs = {
            'doc_ids': [],
            'doc_model': 'stock.picking',
            'docs': line_objs.keys(),
            'line_objs': line_objs
        }
        return report_obj.render(report_name, docargs)
