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
from openerp import models, fields, api


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=80):
        if self._context.get('split', False):
            loc_ids = self._context.get('split', False).split(',')
            args.append(['id', 'in', loc_ids])
        return super(MrpBom, self).name_search(name=name, args=args, operator=operator, limit=limit)


class CopyProductLdm(models.TransientModel):
    _name = 'copy.product.ldm'

    product_ldm_id = fields.Many2one('mrp.bom', string='LdM', required=True)
    ldm_ids_str = fields.Char('LdM ids str', size=255)

    @api.model
    def default_get(self, fields):
        res = super(CopyProductLdm, self).default_get(fields)
        ldm_ids = self.env['mrp.bom'].search([('product_id', '=', self._context.get('active_id', False))])
        stream = []
        if ldm_ids:
            stream = [str(ldm_id.id) for ldm_id in ldm_ids]
            if stream:
                res['ldm_ids_str'] = u', '.join(stream)
            else:
                res['ldm_ids_str'] = '0'
        else:
            res['ldm_ids_str'] = False
        return res

    def _get_bom_lines(self, bom):
        bom_lines = []
        for line_id in bom.bom_line_ids:
            if line_id.product_id.bom_ids:
                x = self._get_bom_lines(line_id.product_id.bom_ids[0])
                for id in x:
                    bom_lines.append(id)
            else:
                bom_lines.append(line_id.id)
        res = list(set(bom_lines))
        return res

    @api.multi
    def copy_ldm_to_ingredients(self):
        for wizard in self:
            bom_lines = []
            if wizard.product_ldm_id.bom_line_ids:
                bom_lines = self._get_bom_lines(wizard.product_ldm_id)
            bom_lines = self.env['mrp.bom.line'].browse(bom_lines)
            for bom_line in bom_lines:
                vals = {
                    'product_parent_id': wizard.product_ldm_id.product_id.id,
                    'product_id': bom_line.product_id.id,
                    'name': bom_line.product_id.name,
                    'product_qty': bom_line.product_qty
                }
                self.env['product.ingredient'].create(vals)
        return {'type': 'ir.actions.act_window_close'}
