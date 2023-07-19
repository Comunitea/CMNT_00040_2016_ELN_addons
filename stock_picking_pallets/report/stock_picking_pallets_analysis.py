# -*- coding: utf-8 -*-
# Copyright 2023 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import tools
from openerp import models, fields

class StockPickingPalletAnalysis(models.Model):
    _name = 'stock.picking.pallet.analysis'
    _auto = False
    _rec_name = 'picking_id'

    picking_id = fields.Many2one(
        'stock.picking', string='Stock Picking', readonly=True)
    date = fields.Datetime('Date', readonly=True)
    partner_id = fields.Many2one(
        'res.partner', string='Partner', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company', readonly=True)
    pallet_type_1 = fields.Integer(string='B1208A-Pallet CHEP 800x1200', readonly=True)
    pallet_type_2 = fields.Integer(string='P0604A-Pallet CHEP 400x600', readonly=True)
    pallet_type_3 = fields.Integer(string='Pallet IPP 800x1200', readonly=True)
    pallet_type_9 = fields.Integer(string='Others types of pallets', readonly=True)
    transport_company_pallets = fields.Integer('Transport company pallets', readonly=True)
    picking_type_code = fields.Char(string='Picking Type Code', readonly=True)

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
            """CREATE or REPLACE VIEW %s as (
            SELECT
                sp.id AS id,
                sp.id as picking_id,
                sp.date_done AS date,
                sp.partner_id as partner_id,
                sp.company_id AS company_id,
                CASE WHEN spt.code in ('incoming', 'internal') THEN sp.pallet_type_1 ELSE -1 * sp.pallet_type_1 END as pallet_type_1,
                CASE WHEN spt.code in ('incoming', 'internal') THEN sp.pallet_type_2 ELSE -1 * sp.pallet_type_2 END as pallet_type_2,
                CASE WHEN spt.code in ('incoming', 'internal') THEN sp.pallet_type_3 ELSE -1 * sp.pallet_type_3 END as pallet_type_3,
                CASE WHEN spt.code in ('incoming', 'internal') THEN sp.pallet_type_9 ELSE -1 * sp.pallet_type_9 END as pallet_type_9,
                CASE WHEN spt.code in ('incoming', 'internal') THEN sp.transport_company_pallets ELSE -1 * sp.transport_company_pallets END as transport_company_pallets,
                spt.code as picking_type_code
            FROM stock_picking sp
            JOIN stock_picking_type spt ON spt.id = sp.picking_type_id
            WHERE sp.state = 'done' and
                (sp.pallet_type_1 > 0 or sp.pallet_type_2 > 0 or sp.pallet_type_3 > 0 or sp.pallet_type_9 > 0 or sp.transport_company_pallets > 0)
            )"""
            % (self._table)
        )
