# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields
import openerp.addons.decimal_precision as dp


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    location_id = fields.Many2one('stock.location', compute="get_lot_location_id")
    uom_id = fields.Many2one(related='product_id.uom_id')
    virtual_available = fields.Float(
        compute='_get_virtual_available',
        type='float',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        string='Not reserved qty')

    @api.model
    def get_location_ids(self, vals):
        id = vals.get('id', False)
        sql = "select sl.id, sl.name || ' / ' || sl2.name as complete_name, sum(qty), rc.name, rc.id "\
              "from stock_quant sq " \
              "join stock_location sl on sl.id = sq.location_id " \
              "join stock_location sl2 on sl2.id = sl.location_id " \
              "join res_company rc on rc.id = sq.company_id " \
              "where sq.lot_id = %s " \
              "group by sl.id, sl.name, sl2.name, rc.name, rc.id" % id
        self._cr.execute(sql)
        records = self._cr.fetchall()
        return records

    @api.multi
    def get_lot_location_id(self, location_id=False):
        for lot in self:
            location_ids = lot.get_location_ids({'id': lot.id})
            location_id = len(location_ids) == 1 and location_ids[0][0]
            lot.location_id = location_id


    @api.model
    def get_available_lot2(self, vals):#version cmnt

        def get_child_of(op_id, active=True):
            sql = "select parent_left, parent_right from stock_location " \
                  "where active = %s and id = (select location_id from stock_move where id = (select min(move_id) from stock_move_operation_link where operation_id = %s))"%(active, op_id)
            self._cr.execute(sql)
            ids = self._cr.fetchone()
            return ids[0], ids[1]

        op_id = vals.get('op_id', 0)
        lot_id = vals.get('lot_id', 0)
        lot_id = lot_id if lot_id != None else 0
        location_id = vals.get('location_ids', 0)
        qty = vals.get('qty', 0.00)
        product_id = vals.get('product_ids', [])[0]
        move_id = vals.get('move_id', [])
        parent_left, parent_right = get_child_of(op_id)

        sql = """
            select count(sq.id) as cuenta, 
                   spl.id as id, 
                   spl.name as display_name, 
                   sum(sq.qty) as qty_available, 
                   sq.location_id as loc_id, 
                   COALESCE(sl.pda_name, sl.complete_name) as location_id, 
                   spl.use_date as use_date, 
                   spl.removal_date as removal_date,
                   (not sq.reservation_id isnull and sq.reservation_id in (select move_id from stock_move_operation_link where operation_id = %s)) as selected, 
                   sq.reservation_id as reservation_id, 
                   pp.pda_name as product_id 
            from stock_quant sq 
            join stock_production_lot spl on spl.id = sq.lot_id 
            join stock_location sl on sl.id = sq.location_id 
            join product_product pp on pp.id = sq.product_id 
            where sq.qty > 0.00 and 
                  (sq.reservation_id isnull or sq.reservation_id in (select move_id from stock_move_operation_link where operation_id = %s) or sq.reservation_id > 0) 
                  and pp.id = %s 
                  and not (spl.id = %s and sq.location_id = %s) 
                  and (sl.parent_left >= %s and sl.parent_right <= %s) 
            group by sq.reservation_id, spl.id, spl.name, sq.location_id, sl.pda_name, sl.complete_name, spl.use_date, sq.company_id, pp.pda_name 
            having sum(sq.qty) >= %s 
            order by selected desc, reservation_id desc, use_date, id
        """ % (op_id, op_id, product_id, lot_id, location_id, parent_left, parent_right, qty)

        self._cr.execute(sql)
        records = self._cr.fetchall()
        lots = []
        for lot_id in records:
            vals = {
                'id': lot_id[1] or 0,
                'display_name': lot_id[2] or False,
                'qty_available': lot_id[3] or 0.00,
                'reservation_id': lot_id[9] or False,
                'loc_id': lot_id[4] or False,
                'location_id': lot_id[5] or False,
                'selected': lot_id[8] or 0,
                'use_date': lot_id[6] or ''
            }
            lots.append(vals)
        return lots

    @api.model
    def get_available_lot(self, vals):#version pedro
        op_id = vals.get('op_id', 0)
        lot_id = vals.get('lot_id', 0)
        lot_id = lot_id if lot_id != None else 0
        product_ids = vals.get('product_ids', [])
        location_id = vals.get('location_id', 0)
        if len(product_ids) == 0:
            return False
        if len(product_ids) == 1:
            product_ids = '(' + str(product_ids[0]) + ')'
        else:
            product_ids = str(tuple(product_ids))
        sql = """
            select * from
                (
                    (
                        select spl.id as id,
                            spl.name as display_name,
                            sum(sq.qty) as qty_available,
                            sl.id as location_id,
                            COALESCE(sl.pda_name, sl.complete_name) as location_id,
                            spl.use_date as use_date,
                            (not sq.reservation_id isnull and sq.reservation_id in (select move_id from stock_move_operation_link where operation_id = %s)) as selected,
                            sq.reservation_id as reservation_id,
                            pp.pda_name as product_name
                        from stock_quant sq
                        join stock_production_lot spl on spl.id = sq.lot_id
                        join stock_location sl on sl.id = sq.location_id
                        join product_product pp on pp.id = sq.product_id 
                        where spl.locked_lot = False
                            and sl.usage = 'internal'
                            and sq.product_id in %s
                            --and not (spl.id = %s and sq.location_id = %s)
                        group by sq.product_id, sl.id, sl.pda_name, sl.complete_name, sq.reservation_id, pp.pda_name, spl.id
                        having sum(sq.qty) > 0.00
                    ) union (
                        select 0 as id,
                            'SIN LOTE' as display_name,
                            sum(sq.qty) as qty_available,
                            sl.id as location_id,
                            COALESCE(sl.pda_name, sl.complete_name) as location_id,
                            null as use_date,
                            (not sq.reservation_id isnull and sq.reservation_id in (select move_id from stock_move_operation_link where operation_id = %s)) as selected,
                            sq.reservation_id as reservation_id,
                            pp.pda_name as product_name
                        from stock_quant sq
                        join stock_location sl on sl.id = sq.location_id
                        join product_product pp on pp.id = sq.product_id 
                        where sq.lot_id is null
                            and sl.usage = 'internal'
                            and sq.product_id in %s
                        group by sq.product_id, sl.id, sl.pda_name, sl.complete_name, sq.reservation_id, pp.pda_name
                        having sum(sq.qty) > 0.00
                    )
                ) available_stock
           order by use_date
        """ % (op_id, product_ids, lot_id, location_id, op_id, product_ids)

        self._cr.execute(sql)
        records = self._cr.fetchall()
        lots = []
        for lot_id in records:
            vals = {
                'id': lot_id[0] or 0,
                'display_name': lot_id[1] or False,
                'qty_available': lot_id[2] or 0.00,
                'reservation_id': lot_id[7] or False,
                'loc_id': lot_id[3] or False,
                'location_id': lot_id[4] or False,
                'selected': lot_id[6] or 0,
                'use_date': lot_id[5] or '',
                'product_name': lot_id[8] or '',
            }
            lots.append(vals)
        return lots

    @api.multi
    def _get_virtual_available(self):
        for lot in self:
            location_ids = [w.view_location_id.id for w in self.env['stock.warehouse'].search([])]
            lot.virtual_available = lot.sudo().product_id.with_context(
                lot_id=lot.id, location=location_ids, force_domain=[('reservation_id','=',False)]).qty_available

