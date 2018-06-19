# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, models, fields, _, tools
import openerp.addons.decimal_precision as dp

from openerp.exceptions import ValidationError


class GroupStockPackOperation(models.Model):

    _name = "stock.pack.operation.group"
    _order = 'picking_order desc'
    _auto = False

    op_id = fields.Many2one('stock.pack.operation', "Ref op para lps datos")
    display_name = fields.Char(related="op_id.display_name", readonly=True)

    package_id = fields.Many2one("stock.quant.package", readonly=True)
    result_package_id = fields.Many2one("stock.quant.package", readonly=True)
    lot_id = fields.Many2one("stock.production.lot", readonly=True)
    pda_product_id= fields.Many2one(related="op_id.pda_product_id", readonly=True)
    ean13 = fields.Char(related='pda_product_id.ean13')
    track_all = fields.Boolean(related="pda_product_id.track_all", readonly=True)
    location_id = fields.Many2one("stock.location", "Origen", readonly=True)
    location_dest_id = fields.Many2one("stock.location", "Destino",  readonly=True)
    product_uom_id = fields.Many2one("product.uom", readonly=True)
    uos_id = fields.Many2one(related="op_id.uos_id", readonly=True)
    qty_done = fields.Float('Quantity Processed', digits_compute=dp.get_precision('Product Unit of Measure'), readonly=True)
    product_qty = fields.Float('Quantity To Process', digits_compute=dp.get_precision('Product Unit of Measure'), readonly=True)
    uos_qty = fields.Float('Quantity To Process(UoS)', digits_compute=dp.get_precision('Product Unit of Measure'), readonly=True, compute="get_uos_qties")
    uos_qty_done = fields.Float('Quantity Processed (UoS)', digits_compute=dp.get_precision('Product Unit of Measure'), compute="get_uos_qties")
    wave_id = fields.Many2one('stock.picking.wave')
    char_op_ids = fields.Char('op id')
    char_picking_ids = fields.Char('picking ids')
    picking_ids = fields.One2many('stock.picking', compute="get_picking_ids")
    op_ids = fields.One2many('stock.pack.operation', compute="get_op_ids")
    picking_names = fields.Char('picking_names')
    pda_done = fields.Boolean("Realizada")
    op_count = fields.Integer("Número de operaciones en la agrupación", readonly=1)
    picking_order = fields.Integer("Picking order", readonly=1)
    group_id = fields.Many2one('stock.pack.operation', "Ref op para lps datos")


    def init(self, cr):

        sql = "select " \
              "spw.id as wave_id, count(op.id) as op_count, min(op.id) as op_id, min(op.id) as id, " \
              "op.pda_done as pda_done, sum(op.product_qty) as product_qty, op.picking_order as picking_order, " \
              "sum(op.qty_done) as qty_done," \
              "op.group_id as group_id," \
              "op.product_uom_id as product_uom_id," \
              "op.location_id as location_id, op.location_dest_id as location_dest_id," \
              "op.lot_id as lot_id, op.package_id as package_id, op.result_package_id as result_package_id, " \
              "string_agg(CAST(sp.name as varchar), ',') as picking_names, " \
              "string_agg(CAST(sp.id as varchar), ',') as char_picking_ids, " \
              "string_agg(CAST(op.id as varchar), ',') as char_op_ids "
        from_cl = "from stock_pack_operation op " \
                 "join stock_picking sp on sp.id = op.picking_id " \
                  "join stock_picking_type spt on spt.id = sp.picking_type_id " \
                  "join stock_picking_wave spw on spw.id = sp.wave_id "
        where_cl = "where sp.state not in ('draft', 'cancel', 'done') and spt.code='internal' "
        group_by = "group by op.package_id, op.result_package_id, spw.id, " \
                   "op.lot_id, op.pda_done, op.location_id, op.location_dest_id, op.picking_order, op.product_uom_id, op.group_id"

        tools.drop_view_if_exists(cr, 'stock_pack_operation_group')
        sql = u"%s %s %s %s"%(sql, from_cl, where_cl, group_by)
        cr.execute(
            """
            CREATE OR REPLACE VIEW stock_pack_operation_group as (
              %s)             
            """ %sql)

    #todo revisar si es necesario sudo
    def get_picking_ids(self):
        self.ensure_one
        picking_ids = [int(x) for x in self.char_picking_ids.split(',')]
        self.picking_ids = [(6, 0, picking_ids)]

    # todo revisar si es necesario sudo
    def get_op_ids(self):
        self.ensure_one
        op_ids = [int(x) for x in self.char_op_ids.split(',')]
        self.op_ids = [(6, 0, op_ids)]

    def get_uos_qties(self):
        t_uom = self.env['product.uom']
        if self.uos_id:
            self.uos_qty_done = t_uom._compute_qty(self.product_uom_id.id,
                                                                    self.qty_done,
                                                                    self.uos_id.id)
            self.uos_qty = t_uom._compute_qty(self.product_uom_id.id,
                                                   self.product_qty,
                                                   self.uos_id.id)

    @api.onchange('qty_done')
    def uom_qty_onchange(self):
        """
        We change uos_qty field
        """
        t_uom = self.env['product.uom']
        if self.env.context.get("skip_uom_qty_onchange"):
            self.env.context = self.with_context(
                skip_uom_qty_onchange=False).env.context
        else:
            if self.uos_id:
                ctx = self._context
                ctx.update(skip_uos_qty_onchange=True)
                self.uos_qty_done = t_uom.with_context(ctx)._compute_qty(self.product_uom_id.id,
                                                                    self.qty_done,
                                                                    self.uos_id.id)

    @api.onchange('uos_qty_done')
    def uos_qty_onchange(self):
        """
        We change quantity field
        """
        t_uom = self.env['product.uom']
        if self.env.context.get("skip_uos_qty_onchange"):
            self.env.context = self.with_context(
                skip_uos_qty_onchange=False).env.context
        else:
            if self.uos_id:
                ctx = self._context
                ctx.update(skip_uom_qty_onchange=True)
                self.qty_done = t_uom.with_context(ctx)._compute_qty(self.uos_id.id,
                                                                    self.uos_qty_done,
                                                                    self.product_uom_id.id)