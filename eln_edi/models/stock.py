# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Pexego All Rights Reserved
#    $Jesús Ventosinos Mayor <jesus@pexego.es>$
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
from openerp import models, api, fields
import openerp.addons.decimal_precision as dp


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    packing_ids = fields.One2many('edi.packing', 'picking_id', 'Packings')

    @api.multi
    def action_print_desadv_label(self):
        p_dic = {}
        edi_obj = self.env['edi.export']
        for picking in self:
            packing_ids = edi_obj.get_packing_ids(picking)
            for k, val in packing_ids.items():
                if picking.id not in p_dic:
                    p_dic[picking.id] = []
                pack_sscc = edi_obj.get_sscc(picking, k)
                pack_gs1_128 = edi_obj.get_gs1_128_barcode_image(str('\xf100') + pack_sscc, width=600, humanReadable=False)
                p_dic[picking.id].append({'product_pack': k,
                                          'total_pack': len(packing_ids),
                                          'pack_sscc': pack_sscc,
                                          'pack_gs1_128': pack_gs1_128
                                          })
        custom_data = {'lines_dic': p_dic}
        rep_name = 'eln_edi.desadv_report'
        rep_action = self.env['report'].get_action(self, rep_name)
        rep_action['data'] = custom_data
        return rep_action
    
    @api.multi
    def modify_edi_packing(self):
        c = self._context.copy()
        c.update(active_model=self._name,
                 active_ids=self._ids,
                 active_id=self._ids[0])
        emp_obj = self.env['edi.modify.packing'].with_context(c)
        created_id = emp_obj.create({})
        return created_id.wizard_view()

    @api.multi
    def restore_edi_packing(self):
        res = self.packing_ids.unlink()
        return res


class EdiPacking(models.Model):
    _name = 'edi.packing'
    _order = 'product_pack, product_id, lot_id'

    picking_id = fields.Many2one('stock.picking', 'Stock Picking',
                                 required=True,
                                 ondelete="cascade",
                                 help='The stock operation where the packing has been made')
    product_id = fields.Many2one('product.product', 'Product')
    product_uom_id = fields.Many2one('product.uom', 'Unit of Measure')
    product_qty = fields.Float('Quantity',
                               digits_compute=dp.get_precision('Product Unit of Measure'),
                               required=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number')
    pack_id = fields.Many2one('edi.pack', 'Pack',
                              required=True,
                              help="Descripción codificada de la forma en la que se presentan los bienes. Se usa en mensaje DESADV. Normalmente código 201.")
    product_pack = fields.Integer('Pack N.')


class EdiPack(models.Model):
    _name = 'edi.pack'

    name = fields.Char('Name', size=64)
    code = fields.Char('Code', size=3)
    note = fields.Text('Notes', readonly = False)

    @api.multi
    def name_get(self):
        return [(edipack.id,
                (edipack.code or '000') + (edipack.name and (' - ' + edipack.name) or ''))
                for edipack in self]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('code', '=', name)] + args, limit=limit)
        if not recs:
            recs = self.search(['|', ('code', operator, name), ('name', operator, name)] + args, limit=limit)
        return recs.name_get()

