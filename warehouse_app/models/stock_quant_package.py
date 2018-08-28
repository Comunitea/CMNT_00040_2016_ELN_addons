# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields
import openerp.addons.decimal_precision as dp



class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    @api.multi
    def get_package_info(self):
        for package in self:
            if package.children_ids:
                package.multi = True
                package.product_id = False
                package.package_qty = 0.00
                package.lot_id = False
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
    uom_id = fields.Many2one(related='product_id.uom_id')

    @api.model
    def get_available_packages(self, vals):
        product_id = vals.get('product_id')
        qty = vals.get('qty')
        domain = [('product_id', '=', product_id), ('multi', '=', False), ('quant_ids', '!=', [])]
        packages = []
        package_ids = self.env['stock.quant.package'].search(domain)

        for package_id in package_ids:
            vals = {'id': package_id.id,
                    'display_name': package_id.display_name,
                    'package_qty': package_id.package_qty,
                    'location_id': package_id.location_id and package_id.location_id.name,
                    'lot_id': package_id.lot_id.name}
            packages.append(vals)
        return packages


    @api.model
    def check_inter(self, old, new):
        return (old.product_id == new.product_id) and new.package_qty > 0

    @api.model
    def name_to_id(self, name):
        package = self.search([('name', '=', name)], limit=1)
        return package or False

    @api.model
    def get_app_fields(self, id):

        object_id = self.browse(id)
        fields = {}
        if object_id:
            for field in fields:
                fields[field] = object_id[field]
        return fields

class StockProductionLot(models.Model):

    _inherit = 'stock.production.lot'

    @api.model
    def get_location_ids(self, vals):
        id = vals.get('id', False)
        sql = "select  sl.id, sl.name || ' / ' || sl2.name as complete_name, sum(qty),rc.name, rc.id from stock_quant sq " \
              "join stock_location sl on sl.id = sq.location_id " \
              "join stock_location sl2 on sl2.id = sl.location_id " \
              "join res_company rc on rc.id = sq.company_id " \
              "where sq.lot_id = %s " \
              "group by sl.id, sl.name, sl2.name, rc.name, rc.id" % id
        print sql
        self._cr.execute(sql)
        records = self._cr.fetchall()
        print records
        return records

    @api.multi
    def get_lot_location_id(self, location_id=False):
        for lot in self:
            location_ids = lot.get_location_ids({'id': lot.id})
            location_id = len(location_ids) == 1 and location_ids[0][0]
            lot.location_id = location_id


    @api.model
    def get_available_lot(self, vals):

        def get_child_of(op_id, active=True):
            sql = "select parent_left, parent_right from stock_location " \
                  "where active = %s and id = (select location_id from stock_move where id = (select min(move_id) from stock_move_operation_link where operation_id = %s))"%(active, op_id)
            self._cr.execute(sql)
            ids = self._cr.fetchone()
            return ids[0], ids[1]

        print vals
        op_id = vals.get('op_id', 0)
        lot_id = vals.get('lot_id', 0)
        location_id = vals.get('location_id', 0)
        qty = vals.get('qty', 0.00)
        product_id = vals.get('product_id', 0)
        move_id = vals.get('move_id', [])
        parent_left, parent_right = get_child_of(op_id)

        ## no uso sql
        sql = "select count(sq.id) as cuenta, spl.id as id, spl.name as display_name, sum(sq.qty) as qty_available, sq.location_id as loc_id, sl.pda_name as location_id, spl.use_date as use_date, spl.removal_date as removal_date, 1 as selected, sq.reservation_id as reservation_id, pp.pda_name as product_id from stock_quant sq " \
              "join stock_production_lot spl on spl.id = sq.lot_id " \
              "join stock_location sl on sl.id = sq.location_id " \
              "join product_product pp on pp.id = sq.product_id " \
              "where sq.reservation_id in (select move_id from stock_move_operation_link where operation_id = %s ) and spl.id = %s and sq.location_id = %s and pp.id = %s " \
              "group by sq.reservation_id, spl.id, spl.name, sq.location_id, sl.pda_name, spl.use_date, sq.company_id, pp.pda_name "  % (op_id, lot_id, location_id, product_id)
        ##distintos lotes y
        sql2 = "select count(sq.id) as cuenta, spl.id as id, spl.name as display_name, sum(sq.qty) as qty_available, sq.location_id as loc_id, sl.pda_name as location_id, spl.use_date as use_date, spl.removal_date as removal_date, " \
               "(not sq.reservation_id isnull  and  sq.reservation_id in (select move_id from stock_move_operation_link where operation_id = %s)) as selected, " \
               "sq.reservation_id as reservation_id, pp.pda_name as product_id from stock_quant sq " \
              "join stock_production_lot spl on spl.id = sq.lot_id " \
              "join stock_location sl on sl.id = sq.location_id " \
              "join product_product pp on pp.id = sq.product_id " \
              "where sq.qty > 0.00 and (sq.reservation_id isnull or sq.reservation_id in (select move_id from stock_move_operation_link where operation_id = %s ) or sq.reservation_id>0) and pp.id = %s " \
              "and not (spl.id = %s and sq.location_id = %s) " \
              "and (sl.parent_left >= %s and sl.parent_right <= %s) " \
              "group by sq.reservation_id, spl.id, spl.name, sq.location_id, sl.pda_name, spl.use_date, sq.company_id, pp.pda_name " \
              "having sum(sq.qty) >= %s " \
              "order by selected desc, reservation_id desc, use_date, id"%(op_id, op_id, product_id, lot_id, location_id, parent_left, parent_right, qty)

        print sql2
        self._cr.execute(sql2)
        records = self._cr.fetchall()
        lots = []
        for lot_id in records:
            vals = {'id': lot_id[1] or 0,
                    'display_name': lot_id[2] or False,
                    'qty_available': lot_id[3] or 0.00,
                    'reservation_id': lot_id[9] or False,
                    'loc_id': lot_id[4] or False,
                    'location_id': lot_id[5] or False,
                    'selected': lot_id[8] or 0,
                    'use_date': lot_id[6] or ''}
            lots.append(vals)
        print lots
        return lots

    @api.multi
    def _get_virtual_available(self):
        for lot in self:
            location_ids = [w.view_location_id.id for w in self.env['stock.warehouse'].search([])]
            lot.virtual_available = lot.sudo().product_id.with_context(lot_id=lot.id, location=location_ids,
                                                                       force_domain=[('reservation_id','=',False)]).qty_available




    location_id = fields.Many2one('stock.location', compute="get_lot_location_id")
    #need_location_check = fields.Boolean('Need location check', compute="get_need_location_check", help ="True si en la primera ubicación padre de tipo vista, hay el mismo lote en distinta ubicación")
    uom_id = fields.Many2one(related='product_id.uom_id')
    virtual_available = fields.Float(
        compute='_get_virtual_available',
        type='float',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        string='Not reserved qty')
