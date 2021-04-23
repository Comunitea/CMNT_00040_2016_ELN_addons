# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp


class StockPickingModifyPacking(models.TransientModel):
    _name = 'stock.picking.modify.packing'

    picking_id = fields.Many2one(
        'stock.picking', 'Picking')
    pack_ul_id = fields.Many2one(
        'product.ul', 'Package Logistic Unit')
    line_ids = fields.One2many(
        'stock.picking.modify.packing.line', 'wiz_id',
        'Lines')

    @api.multi
    def wizard_view(self):
        view = self.env.ref('stock_picking_packing.stock_picking_modify_packing_form')
        return {
            'name': _('Modify packing'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.picking.modify.packing',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': self.env.context,
        }

    @api.model
    def default_get(self, fields):
        res = super(StockPickingModifyPacking, self).default_get(fields)
        picking_id = self._context.get('active_id', False)
        picking = self.env['stock.picking'].browse(picking_id)
        lines = self.get_packing_lines(picking)
        if picking.packing_ids:
            pack_ul_id = picking.packing_ids[0].pack_ul_id
        else:
            pack_ul_id = self.env['product.ul'].search(
                ['|', ('name', 'ilike', 'pallet'), ('name', 'ilike', 'palet')], limit=1)
        res.update(line_ids=lines, picking_id=picking_id, pack_ul_id=pack_ul_id.id)
        return res

    @api.model
    def get_packing_lines(self, picking):
        packing_ids = picking.get_packing_ids()
        lines = []
        for k, vals in packing_ids.items():
            for val in vals:
                lines.append({
                    'product_id': val['product_id'].id,
                    'product_qty': val['product_qty'],
                    'product_uom_id': val['product_uom_id'].id,
                    'product_qty_uos': val['product_qty_uos'],
                    'product_uos_id': val['product_uos_id'].id,
                    'lot_id': val['lot_id'].id,
                    'product_pack': k,
                })
        return lines

    @api.multi
    def modify(self):
        self.picking_id.packing_ids.unlink()
        line_ids = self.line_ids.filtered(lambda r: r.product_qty > 0.0)
        # Verificamos que no se ha variado la cantidad de producto.
        qty_ini = {}
        for line in self.picking_id.pack_operation_ids.filtered(lambda r: r.product_qty > 0.0):
            val_key = (line.product_id.id, line.lot_id.name)
            if val_key in qty_ini:
                qty_ini[val_key] += line.product_qty
            else:
                qty_ini[val_key] = line.product_qty
        qty_fin = {}
        for line in line_ids:
            val_key = (line.product_id.id, line.lot_id.name)
            if val_key in qty_fin:
                qty_fin[val_key] += line.product_qty
            else:
                qty_fin[val_key] = line.product_qty
        if qty_ini != qty_fin:
            raise exceptions.Warning(_('Warning!'),
                _('You can only divide the quantities into different packages, do not add or remove.'))
        line_vals = []
        last_product_pack = 0
        count_pack = 0
        for line in line_ids.sorted(key=lambda a: (a.product_pack, a.product_id, a.lot_id)):
            if last_product_pack <> line.product_pack or count_pack == 0:
                count_pack += 1
                last_product_pack = line.product_pack
            last_product_pack = line.product_pack
            vals = {
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'product_uom_id': line.product_uom_id.id,
                'product_qty_uos': line.product_qty_uos,
                'product_uos_id': line.product_uos_id.id,
                'lot_id': line.lot_id.id,
                'product_pack': count_pack,
                'pack_ul_id': self.pack_ul_id.id
            }
            line_vals.append(vals)
        self.picking_id.write({'packing_ids': [(0, 0, x) for x in line_vals]})
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def auto_default(self):
        self.ensure_one()
        self.line_ids.unlink()
        lines = self.get_packing_lines(self.picking_id.with_context(auto='default'))
        self.write({'line_ids': [(0, 0, line) for line in lines]})
        return self.wizard_view()

    @api.multi
    def auto_pallet(self):
        self.ensure_one()
        self.line_ids.unlink()
        lines = self.get_packing_lines(self.picking_id.with_context(auto='pallet'))
        self.write({'line_ids': [(0, 0, line) for line in lines]})
        return self.wizard_view()

    @api.multi
    def auto_box(self):
        self.ensure_one()
        self.line_ids.unlink()
        lines = self.get_packing_lines(self.picking_id.with_context(auto='box'))
        self.write({'line_ids': [(0, 0, line) for line in lines]})
        return self.wizard_view()


class StockPickingModifyPackingLine(models.TransientModel):
    _name = 'stock.picking.modify.packing.line'
    _order = 'product_pack, product_id, lot_id'

    product_id = fields.Many2one(
        'product.product', 'Product',
        required=True)
    product_qty = fields.Float('Quantity',
        digits=dp.get_precision('Product Unit of Measure'))
    product_uom_id = fields.Many2one(
        'product.uom', 'Unit of Measure')
    product_qty_uos = fields.Float('Quantity (UOS)',
        digits=dp.get_precision('Product UoS'))
    product_uos_id = fields.Many2one(
        'product.uom', 'Product UOS')
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number')
    wiz_id = fields.Many2one(
        'stock.picking.modify.packing', 'Wizard')
    active = fields.Boolean('Active', default=True) 
    product_pack = fields.Integer('Pack N.', default=1)

    @api.multi
    def split(self):
        self.ensure_one()
        res = self.wiz_id.wizard_view()
        if self.product_qty > 1:
            self.product_qty -= 1 
            t_uom = self.env['product.uom']
            product_uos_qty = t_uom._compute_qty(
                self.product_uom_id.id, 1, self.product_uos_id.id)
            self.copy({'product_qty': 1, 'product_qty_uos': product_uos_qty})
        return res

    @api.multi
    def split_uos(self):
        self.ensure_one()
        res = self.wiz_id.wizard_view()
        if self.product_qty_uos > 1:
            self.product_qty_uos -= 1 
            t_uom = self.env['product.uom']
            product_qty = t_uom._compute_qty(
                self.product_uos_id.id, 1, self.product_uom_id.id)
            self.copy({'product_qty': product_qty, 'product_qty_uos': 1})
        return res

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        """
        We change uos_qty field
        """
        t_uom = self.env['product.uom']
        if self.env.context.get('skip_quantity_onchange'):
            self.env.context = self.with_context(
                skip_quantity_onchange=False).env.context
        else:
            if self.product_uos_id:
                self.env.context = self.with_context(
                    skip_uos_qty_onchange=True).env.context
                self.product_qty_uos = t_uom._compute_qty(
                    self.product_uom_id.id, self.product_qty, self.product_uos_id.id)

    @api.onchange('product_qty_uos')
    def onchange_product_qty_uos(self):
        """
        We change quantity field
        """
        t_uom = self.env['product.uom']
        if self.env.context.get('skip_uos_qty_onchange'):
            self.env.context = self.with_context(
                skip_uos_qty_onchange=False).env.context
        else:
            if self.product_uom_id:
                self.env.context = self.with_context(
                    skip_quantity_onchange=True).env.context
                self.product_qty = t_uom._compute_qty(
                    self.product_uos_id.id, self.product_qty_uos, self.product_uom_id.id)

    @api.multi
    def write(self, vals):
        """
        We change product_qty_uos field when split_quantities divide the lines
        """
        res = super(StockPickingModifyPackingLine, self).write(vals)
        if vals.get('product_qty'):
            self.onchange_product_qty()
        if vals.get('product_qty_uos'):
            self.onchange_product_qty_uos()
        return res
