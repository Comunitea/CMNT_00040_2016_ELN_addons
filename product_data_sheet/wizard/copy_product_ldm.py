# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
        technical_sheet_id = self.env['product.technical.sheet'].browse(self._context.get('active_id', False))
        ldm_ids = self.env['mrp.bom'].search([('product_id', '=', technical_sheet_id.product_id.id)])
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
        record_id = self._context.get('active_id', False)
        assert record_id, _('Active Id not found')
        for wizard in self:
            bom_lines = []
            if wizard.product_ldm_id.bom_line_ids:
                bom_lines = self._get_bom_lines(wizard.product_ldm_id)
            bom_lines = self.env['mrp.bom.line'].browse(bom_lines)
            for bom_line in bom_lines:
                vals = {
                    'product_technical_sheet_id': record_id,
                    'product_id': bom_line.product_id.id,
                    'name': bom_line.product_id.name,
                    'product_qty': bom_line.product_qty
                }
                self.env['product.ingredient'].create(vals)
        return {'type': 'ir.actions.act_window_close'}
