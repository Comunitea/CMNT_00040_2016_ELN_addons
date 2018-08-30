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

    @api.model
    def pda_get_destination_for_move(self, vals):
        company_id = vals.get('company_id', False)
        package_id = vals.get('package_id', False)
        location_id = vals.get('location_id', False)
        product_id = vals.get('product_id', False)
        lot_id = vals.get('restrict_lot_id', False)
        models = vals.get('model', [])
        search_str = vals.get('search_str', '')
        ids = []
        res={}

        if 'stock.location' in models:
            sql = "select id, name from stock_location where loc_barcode = '{}' limit 1".format(search_str)
            self._cr.execute(sql)

            location = self._cr.fetchone()
            if location:
                res['location_dest_id'] = {'id': location[0], 'name': location[1]}
                return res

        if 'stock.quant.package' in models:
            package = self.env['stock.quant.package'].search([('name', '=', search_str)])
            if package:
                product_package = package.quant_ids.mapped('product_id')
                if product_id and product_package and product_package != product_id:
                    res['result_package_id'] = {'id': False, 'error': 'Error en el paquete de destino. Tiene otro producto'}
                    return res
                if package.company_id.id != company_id:
                    res['result_package_id'] = {'id': False,
                                                'error': 'Error en el paquete de destino. Company_id'}
                    return res
                res['result_package_id'] = {'id': package.id, 'name': package.name}
                return res

        return False


    @api.model
    def pda_get_available_quants_for_move(self, where=False, vals={}):
        print "pda_get_available_quants_for_move"
        print vals
        company_id = vals.get('company_id', False)
        package_id = vals.get('package_id', False)
        location_id = vals.get('location_id', False)
        product_id = vals.get('product_id', False)
        lot_id = vals.get('restrict_lot_id', False)
        reservation_id = vals.get('reservation_id', False)
        filter= vals.get('filter', False)
        return self.get_available_quants_for_move(where, filter, company_id, package_id, lot_id, product_id, location_id, reservation_id)

    @api.model
    def get_available_quants_for_move(self, add_where=False, filter=False, company_id=False, package_id=False, lot_id=False, product_id=False, location_id=False, reservation_id=False):
        print add_where
        print filter
        where = "where sl.usage = 'internal' "
        if add_where:
            where = "%s %s "%(where, add_where)

        if company_id:
            where = '%s and sq.company_id = %s '%(where, company_id)
        if location_id:
            where = '%s and sq.location_id = %s ' % (where, location_id)
        if package_id:
            where = '%s and sq.package_id = %s ' % (where, package_id)
        if lot_id:
            where = '%s and sq.lot_id = %s ' % (where, lot_id)
        if product_id:
            where = '%s and sq.product_id = %s ' % (where, product_id)
        if company_id or location_id or package_id or lot_id or product_id:
            where = '%s and sq.reservation_id isnull'% where

        if filter:
            if filter['product_ids']:
                where = '%s and sq.product_id in %s ' % (where, tuple(filter['product_ids']))
            if filter['company_ids']:
                where = '%s and rc.id in %s ' % (where, tuple(filter['company_ids']))
            if filter['package_ids']:
                where = '%s and  sq.package_id in %s ' % (where, tuple(filter['package_ids']))
            if filter['lot_ids']:
                where = '%s and  sq.lot_id in %s ' % (where, tuple(filter['lot_ids']))
            if filter['location_ids']:
                where = '%s and  sq.location_id in %s ' % (where, tuple(filter['location_ids']))

        select = "select min(sq.id) as quant_id, sum(sq.qty) as qty_available, " \
                 "spl.id as lot_id, spl.name as lot_name, split_part(spl.use_date::text,' ',1) as use_date, " \
                 "sq.location_id as location_id, sl.name as location_name, sl.loc_barcode, " \
                 "sq.company_id as company_id, rc.name as company_name, " \
                 "pp.id as product_id, pp.name_template as product_name, pp.ean13 as ean13, " \
                 "sqp.id as package_id, sqp.name as package_name, " \
                 "sp.id as picking_id, sp.name as picking_name, sq.reservation_id " \
                 "from stock_quant sq left " \
                 "join stock_location sl on sl.id = sq.location_id left " \
                 "join stock_quant_package sqp on sqp.id = sq.package_id " \
                 "join stock_production_lot spl on spl.id = sq.lot_id " \
                 "join product_product pp on pp.id = sq.product_id " \
                 "join res_company rc on rc.id = sq.company_id " \
                 "left join stock_move sm on sm.id = sq.reservation_id " \
                 "left join stock_picking sp on sp.id = sm.picking_id "
        group = "group by sq.location_id, sq.company_id, sl.name, spl.id, spl.name, sq.product_id, pp.id, pp.name_template, pp.ean13, rc.name, sl.loc_barcode, sqp.id, sqp.name, sq.reservation_id, sp.id, sp.name "
        order = "order by sq.reservation_id desc, use_date, spl.id"
        sql = select + where + group + order
        print sql
        self._cr.execute(sql)
        group_quants = self._cr.fetchall()
        move = {}
        lots = []
        if not group_quants:
            return {'empty':True, 'message': 'Sin coincidencias'}
        move['location_ids'] = []
        move['product_ids'] = []
        move['company_ids'] = []
        move['lot_ids'] = []
        move['package_ids'] = []
        move['picking_ids'] = []
        move['qty'] = 0
        uom_id = {}
        p_ids = []
        l_ids = []
        lt_ids = []
        c_ids = []
        for q in group_quants:
            reservation_id = q[17]
            if q[5] in l_ids:
                location_id = [l_id for l_id in move['location_ids'] if l_id['id'] == q[5]][0]
            else:
                location = self.env['stock.location'].browse(q[5])
                location_id = q[5] and {'id': location.id, 'name': location.pda_name or location.display_name, 'loc_barcode': location.loc_barcode}
                move['location_ids'].append(location_id)
                if not q[17]:
                    l_ids.append(q[5])

            if q[8] in c_ids:
                company_id = [c_id for c_id in move['company_ids'] if c_id['id'] == q[8]][0]
            else:
                company_id = q[8] and  {'id': q[8], 'name': q[9]}
                move['company_ids'].append(company_id)
                if not q[17]:
                    c_ids.append(q[8])

            if q[10] in p_ids:
                product_id = [p_id for p_id in move['product_ids'] if p_id['id'] == q[10]][0]
            else:
                product = self.env['product.product'].browse(q[10])

                uom_id = {'id': product.uom_id.id, 'name': product.uom_id.name}
                product_id = product and {'id': q[10], 'name': product.pda_name or product.name,
                                          'ean13': product.ean13 or False, 'track_all': product.track_all, 'uom_id': uom_id}
                move['product_ids'].append(product_id)
                if not q[17]:
                    p_ids.append(q[10])

            package_id =  q[13] and {'id': q[13], 'name': q[14]}
            if package_id and not package_id in move['package_ids']:
                move['package_ids'].append(package_id)

            picking_id =  q[15] and {'id': q[15], 'name': q[16]}
            if picking_id and not picking_id in move['picking_ids']:
                move['picking_ids'].append(picking_id)

            if q[2] in lt_ids:
                lot_id = [lt_id for lt_id in move['lot_ids'] if lt_id['id'] == q[2]][0]
            else:
                lot_id =  q[2] and {'id': q[2], 'name': q[3], 'use_date': q[4] or False}
                move['lot_ids'].append(lot_id)
                lt_ids.append(q[2])

            quant = {'id': q[0] or False,
                     'qty': q[1] or 0.00,
                     'lot_id':lot_id or False,
                     'location_id':location_id or False,
                     'uom_id': uom_id or False,
                     'company_id': company_id or False,
                     'product_id': product_id or False,
                     'package_id': package_id or False,
                     'picking_id': picking_id or False,
                     'reservation_id': q[17] or False
                     }
            lots.append(quant)

        move['lots'] = lots
        if len(move['lot_ids']) == 1:
            move['product_uom'] = uom_id
            move['qty'] = lots[0]['qty']
        return move





    @api.model
    def get_ids(self, vals):
        def sql_ids(sql, add_where, move):
            self._cr.execute(sql)
            ids = self._cr.fetchall()
            if not ids:
                return False
            len_ids = len(ids)
            if len_ids==0:
                add_where = add_where.format('(0)')
            elif len_ids == 1:
                add_where = add_where.format('(%s)'%ids[0])
            else:
                ids = [x[0] for x in ids]
                add_where = add_where.format(tuple(ids))
            return self.pda_get_available_quants_for_move(add_where, move)

        move = vals.get('move', {})
        models = vals.get('model', [])
        search_str = vals.get('search_str', '')
        limit = vals.get('limit', False)
        domain = vals.get('domain', False)
        if limit:
            limit_str = ' limit %s'%limit
        else:
            limit_str= ''
        ids = {}
        if search_str:
            if 'stock.quant.package' in models:
                sql = "select id from stock_quant_package where name = '%s'%s"%(search_str, limit_str)
                add_where = ' and sqp.id in {}'
                ids = sql_ids(sql, add_where, move)

            if not ids and 'stock.production.lot' in models:
                sql = "select id from stock_production_lot where name = '%s'%s"%(search_str, limit_str)
                add_where = ' and spl.id in {}'
                ids = sql_ids(sql, add_where, move)

            if not ids and 'stock.location' in models:
                sql = "select id from stock_location where loc_barcode = '%s'%s"%(search_str, limit_str)
                add_where = ' and sl.id in {}'
                ids = sql_ids(sql, add_where, move)

            if not ids and 'product.product' in models:
                sql = "select id from product_product where (ean13 = '%s' or dun14 = '%s' or default_code = '%s') %s" %(search_str, search_str, search_str, limit_str)
                add_where = ' and pp.id in {}'
                ids = sql_ids(sql, add_where, move)
        else:
            if move:
                ids = self.pda_get_available_quants_for_move(False, move)
        return ids
