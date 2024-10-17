# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
import odoo.addons.decimal_precision as dp


class StockPackOperation (models.Model):
    _inherit = 'stock.pack.operation'
    order = 'picking_order, product_id, lot_id'

   
    def get_app_names(self):
        for op in self:
            op.pda_product_id = op.product_id or op.lot_id.product_id
            op.total_qty = op.product_id and op.product_qty

    ean13 = fields.Char(related='pda_product_id.ean13')
    picking_order = fields.Char("Picking order")
    loc_row = fields.Char(related='product_id.loc_row', string="Picking order")
    pda_product_id = fields.Many2one('product.product', string="Product", compute=get_app_names)
    pda_done = fields.Boolean ('Pda done', help='True if done from PDA', default=False, copy=False)
    pda_checked = fields.Boolean('Pda checked', help='True if visited in PDA', default=False, copy=False)
    total_qty = fields.Float('Real qty', compute=get_app_names)
    track_all = fields.Boolean(related='pda_product_id.track_all')
    need_confirm = fields.Boolean(related="picking_id.picking_type_id.need_confirm")
    uos_qty = fields.Float('Quantity (S.U.)',
        digits_compute=dp.get_precision('Product Unit of Measure'), compute="get_uos_values", multi=True)
    uos_id = fields.Many2one('product.uom', 'Second Unit', compute="get_uos_values", multi=True)

    @api.model
    def get_need_location_check(self, op_id):
        sql = "select lot_id, location_id from stock_pack_operation where id = %s" % op_id
        self._cr.execute(sql)
        res = self._cr.fetchone()
        lot_id, location_id = res
        parent_location = self.env['stock.location'].get_first_parent_view(location_id)

        sub_location_ids = self.env['stock.location'].browse(parent_location).child_ids.ids
        if lot_id and location_id:
            sql = "select count(location_id) != 1 from stock_quant where lot_id = %s and location_id in %s"%(lot_id,tuple(sub_location_ids))

            self._cr.execute(sql)
            lot_id = self._cr.fetchone()[0]
        return lot_id if lot_id != None else False

   
    def get_uos_values(self):
        t_uom = self.env['product.uom']
        for op in self:
            op.uos_id = op.linked_move_operation_ids and op.linked_move_operation_ids[0].move_id.product_uos or op.pda_product_id.uos_id
            op.uos_qty = t_uom._compute_qty(op.product_uom_id.id, op.product_qty, op.uos_id.id)

    def change_location_dest_id_from_pda(self, id, new_location_id):
        return self.browse([id]).change_location_dest_id(new_location_id)

    def change_location_dest_id(self, new_location_id):
        vals = {'location_dest_id': new_location_id}
        self.write(vals)
        return self.id

    @api.model
    def doOp(self, vals):
        id = vals.get('id', False)
        do_id = vals.get('do_id', True)
        op = self.browse([id])
        qty = vals.get('qty_done', op.qty_done or 0)
        create = vals.get('force_create', False) or True
        if not op:
            return {
                'id': id,
                'error': u'No se ha encontrado la operación'
            }
        if do_id:
            qty_done = float(qty) or op.product_qty
        else:
            qty_done = 0.0

        write_vals = {
            'pda_done': do_id,
            'qty_done': qty_done
        }

        if do_id and create and qty_done < op.product_qty:
            ##REVISAR COMO HAGO UNA OPERACION NUEVA Y VINCULADA AL MOVIMIENTO
            #PROBAR     1 SPLIT DEL MOV
            #           2 GENERAR OPS PARA EL NUEVO MOV
            #           3 RECUPERAR LA OPERACION DEL NUEVO MOV
            qty = op.product_qty - qty_done
            write_vals.update(product_qty=qty_done)
            quants = op.return_quants_to_select(id, qty)
            new_op = []
            for quant in quants:
                if quant[0]:
                    new_op += [op.create_new_op_from_pda(quant)]
            new_id = new_op and new_op[0] or id
            res = op.write(write_vals)
            if not res:
                return_id = id
                aviso = u'Error al actualizar la operación'
            else:
                return_id = new_id
                aviso = u'Nueva operación'

        else:
            res = op.write(write_vals)
            if not res:
                return_id = 0
                aviso = u'Error al actualizar la operación'
            else:
                if do_id:
                    return_id = vals.get('next_id', False)
                    aviso = 'Realizada'
                else:
                    return_id = id
                    aviso = 'Cancelada'

        if return_id > 0:
            res = self.env['stock.pack.operation'].get_op_id({'id': return_id})
        else:
            res = {'id': 0}

        res['aviso'] = aviso
        return res

    def find_next_id(self,vals):
        next_id = 0
        return next_id or 0

    def return_quants_to_select(self, id = False, qty=0):
        quants = []
        move_id = self.linked_move_operation_ids and self.linked_move_operation_ids[0].move_id
        if move_id:
            quants = self.env['stock.quant'].quants_get_prefered_domain(
                move_id.location_id, move_id.product_id,
                qty,
                prefered_domain_list=[[('lot_id', '!=', self.lot_id and self.lot_id.id), ('reservation_id', '=', False)]]
            )
        return quants

    @api.model
    def create_new_op_from_pda(self, quant_tupple):
        quant = quant_tupple[0]
        product_qty = quant_tupple[1]
        if product_qty==0:
            product_qty = self.product_qty - self.qty_done
        new_op = self.copy({
            'product_qty': product_qty,
            'product_id': quant.product_id.id,
            'lot_id': quant.lot_id and quant.lot_id.id,
            'qty_done': 0,
            'pda_done': False,
            'location_id': quant.location_id and quant.location_id.id
        })
        move_id = self.linked_move_operation_ids and self.linked_move_operation_ids[0].move_id
        new_vals = {
            'move_id': move_id.id,
            'operation_id' : new_op.id
        }
        new_link = self.linked_move_operation_ids.create(new_vals)
        self.env['stock.quant'].quants_reserve([quant_tupple], move_id, new_link)
        return new_op.id

    @api.model
    def return_next_op(self, pda_done=False):
        domain=[('picking_id', '=', self.picking_id.id), ('pda_done', '=', not pda_done)]
        ids = self.env['stock.pack.operation'].search_read(domain, ['id'])
        next_id = False
        for id in ids:
            if next_id:
                return id['id']
            if id['id'] == self.id:
                next_id = True
        return 0

   
    def set_pda_done(self):
        for op in self:
            op.pda_done = not op.pda_done
            op.qty_done = op.pda_done and (op.qty_done or op.product_qty) or 0.00

    @api.model
    def change_op_value(self, vals):
        field = vals.get('field', False)
        value = vals.get('value', False)
        id = vals.get('id', False)
        op = self.browse([id])

        res = {'result': False,
               'message': 'Message'}
        if field == 'pda_done':
            op.write({'pda_done': True, 'pda_checked': True})
            res = {'result': True,
                   'message': 'Estado cambiado'}
        elif field == 'pda_checked':
            op.write({'pda_checked': True})
            res = {'result': True,
                   'message': 'Estado cambiado'}
        elif field == 'qty_done':
            new_qty = float(vals.get('value', 0.00))
        elif field == 'location_id':
            new_location_id = self.env['stock.location'].browse(value)
            vals = {'location_id': new_location_id.id}
            if op.write(vals):
                res = {'result': True,
                       'message': 'Nuevo destino %s' % op.location_id.name}
            else:
                res = {'result': False,
                       'message': 'Error al escribir'}

        elif field == 'location_dest_id':
            new_location_dest_id = self.env['stock.location'].browse(value)
            vals = {'location_dest_id': new_location_dest_id.id}

            if op.write(vals):
                res = {'result': True,
                       'message': 'Nuevo destino %s'%op.location_dest_id.name}
            else:
                res = {'result': False,
                       'message': 'Error al escribir'}
        else:
            res = {'result': False,
                   'message': 'Error al escribir'}
        return res

    @api.model
    def get_available_lot(self, vals):
        op = self.browse(vals.get('id'))
        product_id = op.product_id
        lot_ids = self.env['stock.production.lot'].get_lot_ids(op.product_id.id, op.lot_id.id)
        return lot_ids

    @api.model
    def pda_change_lot(self, values):
        lot_id = values.get('lot_id', False)
        op_id = values.get('id', False)
        location_id = values.get('location_id', False)
        force_qty = values.get('force_qty', False)
        op = self.env['stock.pack.operation'].browse(op_id)

        if not location_id:
            return {'result': False, 'message': u"No se ha encontrado la ubicación"}
        if not op:
            return {'result': False, 'message': u"No se ha encontrado la operación"}
        if op.pda_done:
            return {'result': False, 'message': u"La operación ya está realizada"}

        lot = self.env['stock.production.lot'].search_read([('id','=', lot_id)], ['qty_available', 'virtual_available'])

        if not lot:
            return {'result': False, 'message': "No se ha encontrado el lote o es no tiene cantidad"}

        lot = lot[0]

        if not force_qty and (lot['virtual_available'] < op.product_qty or lot['qty_available'] <= 0.00):
            return {'result': False, 'message': u"No hay cantidad suficiente en el lote o está vacío"}

        values = {
            'lot_id': lot_id,
            'pda_done': False,
            'location_id': location_id,
            'qty_done': 0.00
        }
        self.browse(op_id).write(values)
        return op_id

    def dict_m2o(self, val):
        return self.env['warehouse.app'].dict_m2o(val)

    @api.model
    def get_op_id(self, vals):
        return self.env['warehouse.app'].get_op_id(vals)
