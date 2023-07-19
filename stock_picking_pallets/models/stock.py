# -*- coding: utf-8 -*-
# Copyright 2023 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    pallet_type_1 = fields.Integer('B1208A-Pallet CHEP 800x1200')
    pallet_type_2 = fields.Integer('P0604A-Pallet CHEP 400x600')
    pallet_type_3 = fields.Integer('Pallet IPP 800x1200')
    pallet_type_9 = fields.Integer('Others types of pallets')
    transport_company_pallets = fields.Integer('Transport company pallets')
