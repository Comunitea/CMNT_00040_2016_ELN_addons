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
from odoo import models, fields, api, _


class MrpProductionMerge(models.TransientModel):
    _name = 'mrp.production.merge'

    valid_production_id = fields.Many2one(
        'mrp.production', 'Production to keep',
        required=True)
    invalid_production_ids = fields.Many2many(
        'mrp.production', rel='mrp_production_merge_production',
        id1='prod_merge_id', id2='production_id',
        string='Productions to cancel', required=True)

    @api.model
    def default_get(self, fields):
        res = super(MrpProductionMerge, self).default_get(fields)
        if 'active_ids' in self._context and self._context['active_ids']:
            res.update({
                'invalid_production_ids': self._context['active_ids'],
                'valid_production_id': min(self._context['active_ids'])
            })
        return res

   
    def do_merge(self):
        for wizard in self:
            invalid_ids = [x.id for x in wizard.invalid_production_ids]
            new_production_id = wizard.valid_production_id._do_merge(invalid_ids=invalid_ids)
            return {
                'domain': "[('id','=',%d)]" % new_production_id,
                'name': _('Production Orders'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'mrp.production',
                'view_id': False,
                'type': 'ir.actions.act_window'
            }
