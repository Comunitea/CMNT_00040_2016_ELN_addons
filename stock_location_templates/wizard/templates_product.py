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

class templates_product(osv.osv_memory):
    _name = "templates.product"
    _columns = {
        'template_ids': fields.many2many('stock.location.templates', 'location_templates_product_rel','location_template_product_id','template_id','Templates', required=True)

    }
    def assign_templates_to_product(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        form_obj = self.browse(cr, uid, ids, context=context)[0]
        if form_obj.template_ids:
            for template in form_obj.template_ids:
                if template.flow_pull_ids:
                    for pull in template.flow_pull_ids:
                        self.pool.get('product.pulled.flow').copy(cr, uid, pull.id, {'product_id': context['active_ids'][0], 'template_id': False})
            if template.path_ids:
                for path in template.path_ids:
                    self.pool.get('stock.location.path').copy(cr, uid, path.id, {'product_id': context['active_ids'][0], 'template_id': False})
                    
        return {'type': 'ir.actions.act_window_close'}

templates_product()