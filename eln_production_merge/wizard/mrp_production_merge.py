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
from openerp.osv import osv, fields
from openerp.tools.translate import _

class mrp_production_merge(osv.osv_memory):
    _name = "mrp.production.merge"
    _columns = {
        'valid_production_id': fields.many2one('mrp.production', 'Production to keep', required=True),
        'invalid_production_ids': fields.many2many('mrp.production', 'mrp_production_merge_production', 'prod_merge_id', 'production_id', string="Productions to cancel", required=True)
    }

    def default_get(self, cr, uid, fields, context=None):
        """
        """
        res = super(mrp_production_merge, self).default_get(cr, uid, fields, context=context)
        if context and 'active_ids' in context and context['active_ids']:
            res.update({'invalid_production_ids':  context['active_ids']})

        return res

    def do_merge(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for form in self.browse(cr, uid, ids, context=context):
            new_production_id = self.pool.get('mrp.production')._do_merge(cr, uid, [form.valid_production_id.id], [x.id for x in form.invalid_production_ids], context)
            return {
                'domain': "[('id','=',%d)]" % new_production_id,
                'name': _('Production Orders'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'mrp.production',
                'view_id': False,
                'type': 'ir.actions.act_window'
            }


mrp_production_merge()