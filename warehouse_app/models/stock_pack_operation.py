# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, models, fields, _
import openerp.addons.decimal_precision as dp

from openerp.exceptions import ValidationError


class StockPackOperation (models.Model):

    _inherit = 'stock.pack.operation'

    @api.multi
    def get_app_names(self):
        for op in self:
            op.pda_product_id = op.product_id or op.package_id.product_id or op.lot_id.product_id
            op.total_qty = op.product_id and op.product_qty or op.package_id and op.package_id.package_qty
            


    
    picking_order = fields.Integer("Picking order")
    pda_product_id = fields.Many2one('product.product', compute = get_app_names, multi=True)
    pda_done = fields.Boolean ('Pda done', help='True if done from PDA', default=False, copy=False)
    pda_checked = fields.Boolean('Pda checked', help='True if visited in PDA', default=False, copy=False)
    total_qty = fields.Float('Real qty', compute=get_app_names, multi=True)
    track_all = fields.Boolean(related='pda_product_id.track_all')
    need_confirm = fields.Boolean(related="picking_id.picking_type_id.need_confirm")
    uos_qty = fields.Float('Quantity (S.U.)',
                           digits_compute=dp.
                           get_precision('Product Unit of Measure'), compute="get_uos_values", multi=True)
    uos_id = fields.Many2one('product.uom', 'Second Unit', related='product_id.uos_id')

    @api.multi
    def get_uos_values(self):
        t_uom = self.env['product.uom']
        for op in self:
            #op.uos_id = op.move_lines.uos_id.id
            op.uos_id = op.linked_move_operation_ids[0].move_id.product_uos
            op.uos_qty = t_uom._compute_qty(op.product_uom_id.id, op.product_qty, op.uos_id.id)


    def change_package_id_from_pda(self, id, new_package_id):
        return self.browse([id]).change_package_id(new_package_id)

    def change_package_id(self, new_package_id):
        product_id = self.product_id or self.lot_id.product_id
        #Busco nuevo paquete y comprueba si hay existencias y si el paquete = cantidad
        domain = [('id', '=', new_package_id), ('package_qty', '>=', self.product_qty), ('product_id', '=', product_id.id)]
        fields = ['name', 'package_qty', 'location_id', 'lot_id', 'product_id']
        new_package = self.env['stock.quant.package'].search_read(domain, fields)
        new_package = new_package and new_package[0]

        if not new_package or new_package.qty < self.product_qty or new_package.product_id != self.product_id.id:
            raise ValidationError (_('Package not valid'))


        if new_package.qty == self.product_qty:
            vals = {'package_id': new_package.id,
                    'location_id': new_package.location_id and new_package.location_id.id,
                    'qty_done': 0.00,
                    'lot_id': new_package.lot_id and new_package.lot_id.id,
                    'product_id': False}
        else:
            vals = {'package_id': new_package.id,
                    'qty_done': 0.00,
                    'location_id': new_package.location_id  and new_package.location_id.id,
                    'lot_id': new_package.lot_id and new_package.lot_id.id,
                    'product_id': new_package.product_id.id,
                    'product_qty': self.package_id.package_qty}

        self.write(vals)
        return new_package.id


    def change_result_package_id_from_pda(self, id, new_package_id):
        return self.browse([id]).change_result_package_id(new_package_id)

    def change_result_package_id(self, new_package_id):
        product_id = self.product_id or self.lot_id.product_id
        #el paquete no debe tener product_id

        domain = [('id', '=', new_package_id), ('product_id', '=', False)]
        fields = ['name', 'package_qty', 'location_id', 'lot_id', 'product_id']
        new_package = self.env['stock.quant.package'].search_read(domain, fields)
        new_package = new_package and new_package[0]
        if not new_package:
            raise ValidationError (_('Package not valid'))
        vals = {'result_package_id': new_package.id,
                'location_dest_id': new_package.location_id,
                }
        self.write(vals)
        return new_package.id


    def change_location_dest_id_from_pda(self, id, new_location_id):
        return self.browse([id]).change_location_dest_id(new_location_id)

    def change_location_dest_id(self, new_location_id):
        if self.result_package_id and self.result_package_id.location_id.id != new_location_id:
            raise ValidationError(_('Location not valid'))
        vals = {'location_dest_id': new_location_id}
        self.write(vals)
        return self.id

    @api.model
    def doOp(self, vals):
        print"####--- Do op  ---###\n%s\n###############################################" % vals
        id = vals.get('id', False)
        do_id = vals.get('do_id', True)
        op = self.browse([id])
        create = vals.get('force_create', False)
        qty = vals.get('qty_done', op.qty_done or 0)

        if not op:
            return False
        if do_id:
            qty_done = float(qty) or op.product_qty
        else:
            qty_done = 0.0

        vals = {'pda_done': do_id,
                 'qty_done': qty_done}
        op.write(vals)

        if create:
            quants = op.return_quants_to_select(id, op.product_qty - qty_done)
            new_op = []
            for quant in quants:
                new_op += [op.create_new_op_from_pda(quant, op.get_result_package())]
            if new_op:
                return new_op[0]
        return op.id

    def get_result_package(self):
        #POara heredar si es necesario
        if self.result_package_id:
            return self.result_package_id.create({}).id
        else:
            return False


    def return_quants_to_select(self, id = False, qty=0):
        quants = []
        move_id = self.linked_move_operation_ids and self.linked_move_operation_ids[0].move_id
        if move_id:
            quants = self.env['stock.quant'].quants_get_prefered_domain(move_id.location_id, move_id.product_id,
                                                                        qty,
                                                                        prefered_domain_list=[[('reservation_id', '=', False)]])
        return quants

    @api.model
    def create_new_op_from_pda(self, quant_tupple, result_package_id = False):
        import ipdb; ipdb.set_trace()

        quant = quant_tupple[0]
        product_qty = quant_tupple[1]
        if product_qty==0:
            product_qty = self.product_qty - self.qty_done

        if quant.package_id and product_qty == quant.package_qty:
            new_op = self.copy({
                'product_qty': product_qty,
                'product_id': False,
                'package_id': quant.package_id and quant.package_id.id,
                'lot_id': quant.package_id.lot_id and quant.package_id.lot_id.id,
                'location_id': quant.package_id.location_id and quant.package_id.location_id.id})
        else:
            new_op = self.copy({
                'product_qty': product_qty,
                'product_id': quant.product_id.id,
                'package_id': quant.package_id and quant.package_id.id,
                'result_package_id': result_package_id,
                'lot_id': quant.lot_id and quant.lot_id.id,
                'location_id': quant.location_id and quant.location_id.id})

        move_id = self.linked_move_operation_ids and self.linked_move_operation_ids[0].move_id
        new_vals = {'move_id': move_id.id,
                   'operation_id' : new_op.id}
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
            print "comparo %s con %s"%(self.id, id['id'])
            if id['id'] == self.id:
                next_id = True
                print "Nexr op:%s"%next_id
        return 0


    def get_new_pack_values(self):
        return {'location_id': self.location_dest_id.id}

    @api.multi
    def put_in_pack(self):
        for op in self.filtered(lambda x:not x.result_package_id and x.location_dest_id.in_pack):
            if not op.result_package_id:
                op.result_package_id = self.env['stock.quant.package'].create(op.get_new_pack_values())

    @api.one
    def set_pda_done(self):
        print  "####--- Marcar la operacion como realizada %s ---###\n###############################################"%self.id
        self.pda_done = not self.pda_done
        if self.pda_done and not self.result_package_id:
            self.put_in_pack()


    @api.model
    def change_op_value(self, vals):
        print  "####--- Cambiar valores en las operaciones ---###\n###############################################\n%s"%vals
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
            print "Cambiar cantidad"
            new_qty = float(vals.get('value', 0.00))
            if op.package_id.package_qty > new_qty:
                if op.product_id:
                    op_vals = {'qty_done': new_qty}
                else:
                    op_vals = {'qty_done': new_qty,
                              'product_qty': new_qty,
                              'product_id': op.package_id.product_id.id,
                              'product_uom_id': op.package_id.product_id.uom_id.id,
                              'lot_id': op.package_id.lot_id and op.package_id.lot_id.id}
                op_ok = op.write(op_vals)
                res = {'result': True,
                       'message': 'Cantidad hecha:%s' % op.qty_done}
            elif op.package_id.package_qty == new_qty:
                #si es mayor >> entonces movemos el paquete completo
                op.write({'product_id': False,
                          'product_qty': 1,
                          'lot_id': False,
                          'qty_done': 1})
                res = {'result': True,
                       'message': 'Paquete completo'}
            elif op.package_id.package_qty < new_qty:
                #si es mayor >> entonces movemos el paquete completo
                op.write({'product_id': False,
                          'lot_id': False,
                          'product_qty': 1,
                          'qty_done': 1})
                #3crear una nueva operacion por que no llega
                res = {'result': True,
                       'message': 'No hay suficiente cantidad en el paquete'}

        elif field == 'package_id':
            print "Cambiar paquete origen"
            new_package = self.env['stock.quant.package'].browse([value])
            if self.env['stock.quant.package'].check_inter(op.package_id, new_package):
                new_op = self.op_change_package(op, value)
                if new_op:
                    res = {'result': True,
                           'new_op': new_op,
                           'message': 'Ops rehechas. Actualizado listado de operaciones'}
                else:
                    res = {'result': False,
                           'message': 'Error. Revisa desde ERP'}

            else:
                res = {'result': False,
                       'message': 'Paquete incompatible'}

        elif field == 'location_id' and (not op.package_id or (op.package_id and op.package_id.location_id)):
            print "Cambiar Destino"
            new_location_id = self.env['stock.location'].browse(value)
            vals = {'location_id': new_location_id.id}
            if op.write(vals):
                res = {'result': True,
                       'message': 'Nuevo destino %s' % op.location_id.name}
            else:
                res = {'result': False,
                       'message': 'Error al escribir'}

        elif field == 'location_dest_id' and (not (op.result_package_id and op.result_package_id.location_id)):
            print "Cambiar DXestino"
            new_location_dest_id = self.env['stock.location'].browse(value)
            vals = {'location_dest_id': new_location_dest_id.id}

            if op.write(vals):
                res = {'result': True,
                       'message': 'Nuevo destino %s'%op.location_dest_id.name}
            else:
                res = {'result': False,
                       'message': 'Error al escribir'}

        elif field == 'result_package_id':
            print "Cambiar paquete de destino"
            new_package = self.env['stock.quant.package'].browse(value)
            if not new_package.multi:
                location_dest_id = new_package.location_id and new_package.location_id.id or op.location_dest_id.id
                vals = {'result_package_id': new_package.id}
                if new_package.location_id:
                    vals['location_dest_id'] = new_package.location_id.id

                if op.write(vals):
                    res = {'result': True,
                           'message': 'Nuevo destino %s' % op.result_package_id.name}
                else:
                    res = {'result': False,
                           'message': 'Error al escribir'}
            else:
                res = {'result': False,
                       'message': 'Paquete de destino no válido'}


        else:
            res = {'result': False,
                   'message': 'Error al escribir'}
        return res


    @api.model
    def op_change_package(self, op, new_package):
        move_ids = op.linked_move_operation_ids.mapped('move_id')
        if all(move.state in ('confirmed', 'assigned') for move in move_ids):
            for move in move_ids:
                ctx = op._context.copy()
                op.unlink()
                move.do_unreserve()
                self.env['stock.quant'].quants_unreserve(move)
                ctx.update({'new_package_id': new_package})
                move.with_context(ctx).action_assign()
                return move.move_prepare_partial()


    @api.model
    def get_available_lot(self, vals):
        print "recuperando quants"
        op = self.browse(vals.get('id'))
        print "para la op %s"%op
        product_id = op.product_id
        lot_ids = self.env['stock.production.lot'].get_lot_ids(op.product_id.id, op.lot_id.id)
        print lot_ids
        return lot_ids



    @api.model
    def pda_change_lot(self, values):
        lot_id = values.get('lot_id')
        op_id = values.get('id')

        lot = self.env['stock.production.lot'].search_read([('id','=', lot_id)], ['location_id'])
        if op_id and lot and lot[0]['location_id']:
            values = {'lot_id': lot_id, 'location_id': lot[0]['location_id'][0], 'pda_done': False, 'qty_done': 0.00}
            self.browse(op_id).write(values)
            return op_id
        return False


    @api.model
    def pda_change_package(self, values):

        package_id = values.get('package_id')
        op_id = values.get('id', 0)
        op = self.env['stock.quant.operation'].browse(op_id)
        package = self.env['stock.quant.package'].search_read([('id', '=', package_id)],
                                                              ['product_id', 'location_id', 'lot_id', 'qty',
                                                               'package_qty'])
        if not op:
            return {'result': False, 'message': "No se ha encontrado la operación"}

        if op.pda_done:
            return {'result': False, 'message': "La operación ya está realizada"}

        package = package and package[0]

        if not package or package.multi:
            return {'result': False, 'message': "No se ha encontrado el paquete o es multiproducto"}

        if op.product_id != package.product_id and op.product_id.is_sustitutive(package.product_id.id):

            if op.product_qty:
                qty = op.package_id.package_qty
            else:
                qty = op.product_qty

            if package.package_qty == qty:
                qty = 1
                product_id = False
            else:
                qty = package.package_qty
                product_id = op.package_id.product_id.id

            values = {'lot_id':  package.lot_id.id,
                      'location_id': package.location_id.id,
                      'package_id': package.id,
                      'pda_done': False,
                      'product_id': product_id,
                      'product_qty': qty,
                      'qty_done': 0.00,
                      'location_dest_id': op.location_dest_id.id,
                      'result_package_id': op.result_package_id and op.result_package_id.id,
                      'uom_id': package.product_id.uom_id.id,
                      'picking_id': op.picking_id.id
                      }
            op.unlink()
            new_op = self.create(values)
            return {'result': True, 'new_op': new_op.id}

        elif op.product_id == package.product_id:

            if op.product_qty:
                qty = op.package_id.package_qty
            else:
                qty = op.product_qty

            if package.package_qty == qty:
                qty = 1
                product_id = False
            else:
                qty = package.package_qty
                product_id = op.package_id.product_id.id

            values = {'lot_id':  package.lot_id.id,
                      'location_id': package.location_id.id,
                      'package_id': package.id,
                      'pda_done': False,
                      'product_id': product_id,
                      'product_qty': qty,
                      'qty_done': 0.00,
                      'location_dest_id': op.location_dest_id.id,
                      'resulta_package_id': op.result_package_id and op.result_package_id.id,
                    }
            res = op.write(values)
            return {'result': res, 'new_op': False}

        return False