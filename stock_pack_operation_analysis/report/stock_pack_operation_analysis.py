# -*- coding: utf-8 -*-
# Copyright 2017 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import tools
from openerp import models, fields
from openerp.osv import osv

class StockPackOperationAnalysis(models.Model):
    _name = 'stock.pack.operation.analysis'
    _auto = False
    _rec_name = 'product_id'

    product_id = fields.Many2one(
        'product.product', string='Product', readonly=True)
    lot_id = fields.Many2one(
        'stock.production.lot', string='Lot/Serial Number', readonly=True)
    product_qty = fields.Float(string='Quantity', readonly=True)
    picking_id = fields.Many2one(
        'stock.picking', string='Stock Picking', readonly=True)
    date = fields.Datetime('Date', readonly=True)
    partner_id = fields.Many2one(
        'res.partner', string='Partner', readonly=True)
    location_id = fields.Many2one(
        'stock.location', string='Source Location', readonly=True)
    location_dest_id = fields.Many2one(
        'stock.location', string='Destination Location', readonly=True)
    categ_id = fields.Many2one(
        'product.category', string='Internal Category', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company', readonly=True)

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
            """CREATE or REPLACE VIEW %s as (
            SELECT
                spo.id AS id,
                spo.product_id AS product_id,
                spo.date AS date,
                spo.product_qty as product_qty,
                spo.lot_id as lot_id,
                sp.id as picking_id,
                sp.partner_id as partner_id,
                spo.location_id as location_id,
                spo.location_dest_id as location_dest_id,
                pt.categ_id as categ_id,
                sp.company_id AS company_id
            FROM stock_pack_operation AS spo
            JOIN stock_picking sp ON sp.id = spo.picking_id
            JOIN product_product pp on pp.id = spo.product_id
            JOIN product_template pt on pt.id = pp.product_tmpl_id
            WHERE sp.state = 'done'
            )"""
            % (self._table)
        )
