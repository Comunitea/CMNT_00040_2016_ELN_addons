# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, models, fields
import openerp.addons.decimal_precision as dp

from openerp.exceptions import ValidationError

class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    @api.multi
    def get_package_info(self):
        for package in self:
            if package.children_ids:
                package.multi = True
                package.product_id = False
                package.package_qty = 0.00
                lot_id = False
            else:
                package.multi = False
                package.package_qty = sum(quant.qty for quant in package.quant_ids)
                package.product_id = package.quant_ids and package.quant_ids[0].product_id or False
                package.lot_id = package.quant_ids and package.quant_ids[0].lot_id or False

    package_qty = fields.Float('Quantity',
                               digits_compute=dp.get_precision('Product Unit of Measure'),
                               compute=get_package_info, multi=True)
    product_id = fields.Many2one('product.product', 'Product', compute=get_package_info, multi=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot', compute=get_package_info, multi=True)
    multi = fields.Boolean('Multi', compute=get_package_info, multi=True)
    product_id_name = fields.Char(related='product_id.display_name')

    @api.model
    def check_inter(self, old, new):
        return (old.product_id == new.product_id) and new.package_qty > 0

    @api.model
    def name_to_id(self, name):
        package = self.search([('name','=',name)], limit=1)
        return package or False

class StockPackOperation (models.Model):

    _inherit = 'stock.pack.operation'

    @api.multi
    def get_app_names(self):
        for op in self:
            op.pda_product_id = op.product_id or op.package_id.product_id or op.lot_id.product_id

            op.product_uom = op.product_id and op.product_id.uom_id
            op.total_qty = op.product_id and op.product_qty or op.package_id and op.package_id.package_qty
            op.real_lot_id = op.lot_id or op.package_id.lot_id

    #package_id_name = fields.Char(related='package_id.name')
    location_dest_id_barcode =  fields.Char(related='location_dest_id.loc_barcode')
    location_id_barcode = fields.Char(related="location_id.loc_barcode")
    #result_package_id_name = fields.Char(related='result_package_id.name')
    pda_product_id = fields.Many2one('product.product', compute = get_app_names, multi=True)
    product_uom = fields.Many2one('product.uom', compute = get_app_names, multi=True)
    pda_done = fields.Boolean ('Pda done', help='True if done from PDA')
    pda_checked = fields.Boolean('Pda checked', help='True if visited in PDA')
    total_qty = fields.Float('Real qty', compute=get_app_names, multi=True)
    real_lot_id = fields.Many2one('stock.production.lot', 'Real lot', compute=get_app_names, multi=True)
    #lot_id_name = fields.Char(related='real_lot_id.name')
    #orig_package_id = fields.Many2one('stock.quant.package', 'Orig. package')
    #orig_lot_id = fields.Many2one('stock.production.lot', 'Orig. lot')
    #orig_qty = fields.Float('Orig qty')

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
                    'location_id': new_package.location_id,
                    'lot_id': new_package.lot_id,
                    'product_id': False}
        else:
            vals = {'package_id': new_package.id,
                    'location_id': new_package.location_id,
                    'lot_id': new_package.lot_id,
                    'product_id': new_package.product_id,
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
        qty = vals.get('qty', op.qty_done or 0)


        if not op:
            return False
        if do_id:
            qty_done = qty or op.product_qty
        else:
            qty_done = 0.00
        op.write({'pda_done': do_id,
                 'qty_done': qty_done})
        return True

    def get_new_pack_values(self):
        return {'location_id': self.location_dest_id.id}

    @api.multi
    def put_in_pack(self):
        for op in self.filtered(lambda x:not x.result_package_id):
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
                              'lot_id': op.package_id.lot_id.id}
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

        elif field == 'location_id' and not op.package_id:
            print "Cambiar DXestino"
            new_location_id = self.env['stock.location'].browse(value)
            vals = {'location_id': new_location_id.id}

            if op.write(vals):
                res = {'result': True,
                       'message': 'Nuevo destino %s'%op.location_id.name}
            else:
                res = {'result': False,
                       'message': 'Error al escribir'}

        elif field == 'location_dest_id' and not op.result_package_id:
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



