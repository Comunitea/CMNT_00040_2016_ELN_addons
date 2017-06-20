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
from openerp import _, api, exceptions, fields, models
import openerp.addons.decimal_precision as dp


class EdiModifyPackingLine(models.TransientModel):
    _name = 'edi.modify.packing.line'
    _order = 'product_pack, product_id, lot_id'

    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_qty = fields.Float('Quantity',
        digits=dp.get_precision('Product Unit of Measure'))
    product_uom_id = fields.Many2one('product.uom', 'Unit of Measure')
    lot_id = fields.Many2one('stock.production.lot', 'Lot')
    wiz_id = fields.Many2one('edi.modify.packing', 'Wizard')
    active = fields.Boolean('Active', default=True) 
    product_pack = fields.Integer('Pack N.', default=1)

    @api.multi
    def split(self):
        self.ensure_one()
        res = self.wiz_id.wizard_view()
        if self.product_qty > 1:
            self.product_qty -= 1 
            self.copy({'product_qty': 1})
        return res


class EdiModifyPacking(models.TransientModel):
    _name = 'edi.modify.packing'

    picking_id = fields.Many2one('stock.picking', 'Picking')
    pack_id = fields.Many2one('edi.pack', 'Pack', required=True,
          help="Descripción codificada de la forma en la que se presentan los bienes. Se usa en mensaje DESADV. Normalmente código 201.")
    line_ids = fields.One2many('edi.modify.packing.line', 'wiz_id', 'Lines')

    @api.multi
    def wizard_view(self):
        view = self.env.ref('eln_edi.edi_modify_packing_form')
        return {
            'name': _('Modify EDI packing'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'edi.modify.packing',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': self.env.context,
        }

    @api.model
    def default_get(self, fields):
        res = super(EdiModifyPacking, self).default_get(fields)
        picking_id = self._context.get('active_id', False)
        picking = self.env['stock.picking'].browse(picking_id)
        lines = []
        if picking.packing_ids:
            pack = picking.packing_ids[0].pack_id
            for line in picking.packing_ids:
                lines.append({'product_id': line.product_id.id,
                              'product_qty': line.product_qty, 
                              'product_uom_id': line.product_uom_id.id, 
                              'product_pack': line.product_pack,
                              'lot_id': line.lot_id.id})
        else:
            pack = self.env['edi.pack'].search([('code', '=', '201')], limit=1) # Por defecto
            for line in picking.pack_operation_ids.filtered(lambda r: r.product_qty > 0.0):
                lines.append({'product_id': line.product_id.id,
                              'product_uom_id': line.product_uom_id.id, 
                              'product_qty': line.product_qty, 
                              'product_pack': 1,
                              'lot_id': line.lot_id.id})
        res.update(line_ids=lines, picking_id=picking_id, pack_id=pack.id)
        return res

    @api.multi
    def modify(self):
        self.picking_id.packing_ids.unlink()
        line_ids = self.line_ids.filtered(lambda r: r.product_qty > 0.0)
        # Verificamos que no se ha variado la cantidad de producto
        # Solo se puede repartir entre paquetes
        qty_ini = {}
        qty_fin = {}
        for line in self.picking_id.pack_operation_ids.filtered(lambda r: r.product_qty > 0.0):
            val_key = (line.product_id.id, line.lot_id.name)
            if val_key in qty_ini:
                qty_ini[val_key] += line.product_qty
            else:
                qty_ini[val_key] = line.product_qty
        for line in line_ids:
            val_key = (line.product_id.id, line.lot_id.name)
            if val_key in qty_fin:
                qty_fin[val_key] += line.product_qty
            else:
                qty_fin[val_key] = line.product_qty
        if qty_ini != qty_fin:
            raise exceptions.Warning(_("Warning!"), _("You can only divide the quantities into different packages, do not add or remove."))
            return self.wizard_view()
        
        line_vals = []
        last_product_pack = 0
        count_pack = 0
        for line in line_ids.sorted(key=lambda a: (a.product_pack, a.product_id, a.lot_id)):
            if last_product_pack <> line.product_pack or count_pack == 0:
                count_pack += 1
                last_product_pack = line.product_pack
            last_product_pack = line.product_pack
            vals = {'product_id': line.product_id.id,
                    'product_uom_id': line.product_uom_id.id,
                    'product_qty': line.product_qty,
                    'lot_id': line.lot_id.id,
                    'product_pack': count_pack,
                    'pack_id': self.pack_id.id}
            line_vals.append(vals)
        self.picking_id.write({'packing_ids': [(0, 0, x) for x in line_vals]})
        return {'type': 'ir.actions.act_window_close'}
