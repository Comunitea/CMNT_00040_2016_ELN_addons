# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields

from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare, float_round

class StockMove(models.Model):
    _inherit = "stock.move"

    restrict_package_id = fields.Many2one('stock.quant.package', string="From package")
    result_package_id = fields.Many2one('stock.quant.package', string="To package")
    package_qty = fields.Boolean('Package qty')

    def pda_onchange_lot(self):
        return

    def onchange_result_package_id(self, cr, uid, ids, result_package_id=False, context=None):
        if result_package_id:
            package = self.pool.get('stock.quant.package').browse(cr, uid, [result_package_id], context=context)
            if package:
                result = {'location_dest_id': package.location_id.id}
                return {'value': result}

    def onchange_package_qty(self, cr, uid, ids, package_qty=False, restrict_package_id=False, context=None):
        if restrict_package_id and package_qty:
            package = self.pool.get('stock.quant.package').browse(cr, uid, [restrict_package_id], context=context)
            result = {'product_uom_qty': package.package_qty}
        else:
            result = {'product_uom_qty': 1}
        return {'value': result}

    def onchange_restrict_package_id(self, cr, uid, ids, restrict_package_id=False, location_dest_id=False, partner_id=False, context=None):

        if not restrict_package_id:
            return {'value': {'package_qty': False}}

        context = context.copy()
        context.update(cancel_event=True)
        package = self.pool.get('stock.quant.package').browse(cr, uid, [restrict_package_id], context=context)
        if package and not package.multi and package.product_id:
            res = self.onchange_product_id(cr, uid, ids,
                                           prod_id=package.product_id.id,
                                           loc_id=package.location_id.id,
                                           loc_dest_id=location_dest_id,
                                           partner_id=partner_id)
            res['value']['product_id'] = package.product_id.id
            res['value']['product_uom_qty'] = package.package_qty
            res['value']['product_uos_qty'] = self.onchange_quantity(cr, uid, ids, package.product_id.id, package.package_qty, package.product_id.uom_id.id, package.product_id.uos_id.id)['value']['product_uos_qty']
            if package.product_id.track_all:
                res['value']['restrict_lot_id'] = package.lot_id.id
            res['value']['restrict_package_id'] = restrict_package_id
            res['value']['result_package_id'] = restrict_package_id
            res['value']['package_qty'] = True
            print res

            return res
        else:
            value = {'product_id': False, 'product_uom_qty': 0, 'restrict_lot_id': False, 'restrict_package_id': False, 'location_id': False}
            return {'value': value}


    @api.model
    def move_prepare_partial(self):
        #NO SE USA
        forced_qties = {}
        if self.state not in ('assigned', 'confirmed', 'waiting'):
            return
        quants = self.reserved_quant_ids

        forced_qty = (self.state == 'assigned') and self.product_qty - sum([x.qty for x in quants]) or 0
        # if we used force_assign() on the move, or if the move is incoming, forced_qty > 0
        if float_compare(forced_qty, 0, precision_rounding=self.product_id.uom_id.rounding) > 0:
            if forced_qties.get(self.product_id):
                forced_qties[self.product_id] += forced_qty
            else:
                forced_qties[self.product_id] = forced_qty
        for vals in self.picking_id._prepare_pack_ops(self.picking_id, quants, forced_qties):
            new_op = self.env['stock.pack.operation'].create(vals)

        self.picking_id.do_recompute_remaining_quantities()
        self.picking_id.write({'recompute_pack_op': False})
        return new_op and new_op.id or False


    @api.multi
    def action_assign(self):
        return super(StockMove, self).action_assign()


    @api.multi
    def action_done(self):
        ctx = self._context.copy()
        for move in self:
            ctx = move._context.copy()
            if move.restrict_package_id:
                move.restrict_lot_id = move.restrict_package_id.lot_id
                ctx.update({'new_package_id': move.restrict_package_id.id})
            if move.result_package_id:
                ctx.update({'result_package_id': move.result_package_id.id})
        return super(StockMove, self.with_context(ctx)).action_done()

    @api.model
    def pda_move(self, vals):
        company_id = vals.get('company_id', False)
        product_id = vals.get('product_id', False)
        product_id = self.env['product.product'].get_pda_product(product_id)
        location_id = vals.get('location_id', False)

        if not company_id:
            company_id = product_id.company_id.id
        user_id = self.sudo().env['res.company'].browse(company_id).intercompany_user_id
        self = self.sudo(user_id.id)
        if self.env.user.company_id.id != company_id:
            return {'message': 'Error de intercompañia', 'id': 0}

        restrict_package_id = vals.get('restrict_package_id', False)
        location_dest_id = vals.get('location_dest_id', False)
        result_package_id = vals.get('result_package_id', False)
        create_new_result = False
        package_qty = vals.get('package_qty', False)
        product_uom_qty = vals.get('product_qty', 0.00)

        if restrict_package_id and restrict_package_id == result_package_id and not package_qty:
            return {'message': 'No puedes mover un paquete si no es completo', 'id': 0}
        if product_uom_qty <=0:
            return {'message': 'No puedes una cantidad menor o igual a 0', 'id': 0}

        if result_package_id == 0:
            result_package_id = False
        if result_package_id:
            if result_package_id > 0 and result_package_id != restrict_package_id:
                result_package_id = self.env['stock.quant.package'].browse(result_package_id)

                if result_package_id.location_id and result_package_id.location_id.id != location_dest_id:
                    return {'message': 'No puedes mover a un paquete que no está en la ubicación de destino', 'id': 0}
                location_dest_id = location_dest_id
                result_package_id = result_package_id.id
            elif result_package_id < 0:
                create_new_result = True


        if restrict_package_id:
            ##Paquete de origen
            restrict_package_id = self.env['stock.quant.package'].browse(restrict_package_id)
            restrict_lot_id = restrict_package_id.lot_id and restrict_package_id.lot_id.id
            product_id = restrict_package_id.product_id
            if package_qty:
                product_uom_qty = restrict_package_id.package_qty
            location_id = restrict_package_id.location_id.id
            if not result_package_id and not create_new_result and package_qty:
                result_package_id = restrict_package_id.id

        else:
            ##Sin paquete de origen
            restrict_lot_id = vals.get('restrict_lot_id', False)

        if create_new_result:
            result_package_id = self.env['stock.quant.package'].create({}).id

        vals = {
            'origin': 'PDA done: [%s]'%self.env.user.name,
            'restrict_package_id': restrict_package_id and restrict_package_id.id,
            'restrict_lot_id': restrict_lot_id,
            'product_id': product_id.id,
            'product_uom': product_id.uom_id.id,
            'product_uom_qty': product_uom_qty,
            'name': product_id.display_name,
            'location_id': location_id,
            'result_package_id': result_package_id,
            'location_dest_id': location_dest_id
        }

        print vals
        new_move = self.env['stock.move'].create(vals)

        if new_move:
            print "PDA Move creado con id %s" % new_move.id
            new_move.action_done()
            res = {'message': 'OK', 'id': new_move.id}
        else:
            res = {'message': 'Error al crear el movimiento', 'id': 0}
        print res
        return res
