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

class process_expedient(osv.osv):

    _name = "process.expedient"

    def process_expedient(self, cr, uid, ids, context=None):
        if context is None: context = {}
        expedient_ids = context.get('active_ids', [])
        for expedient in expedient_ids:
            self.pool.get('expedient').validate_expedient(cr, uid, [expedient])
            exp_obj = self.pool.get('expedient').browse(cr, uid, expedient)
            if exp_obj.state == "completed" and not exp_obj.parent_expedient:
                self.pool.get('expedient').create_final_expedient(cr, uid, [exp_obj.id])

        return {'type': 'ir.actions.act_window_close'}

process_expedient()
