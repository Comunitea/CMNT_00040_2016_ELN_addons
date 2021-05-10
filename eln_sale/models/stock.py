# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    supplier_id = fields.Many2one(
        string="Supplier",
        comodel_name='res.partner',
        readonly=True, select=True,
        domain = [('supplier','=',True)],
        states={'draft': [('readonly', False)]})
    carrier_id = fields.Many2one(
        string="Carrier",
        comodel_name='res.partner',
        readonly=True, select=True,
        states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)], 'assigned': [('readonly', False)]})
    requested_date = fields.Date(
        string='Requested Date',
        states={'cancel': [('readonly', True)]},
        help="Date by which the customer has requested the items to be delivered.")
    effective_date = fields.Date(
        string='Effective Date',
        readonly=True,
        states={'done': [('readonly', False)]},
        default=fields.Datetime.now,
        help="Date on which the delivery order was delivered.")
    supplier_cip = fields.Char(
        string='CIP',
        related="sale_id.supplier_cip",
        readonly=True,
        help="Internal supplier code")
    sent_to_supplier = fields.Boolean(
        string='Sent to Supplier',
        readonly=True,
        states={'done': [('readonly', False)], 'cancel': [('readonly', False)]},
        default=False,
        help="Check this box if the physical delivery note has been sent to the supplier")

    @api.multi
    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        if 'effective_date' in vals:
            orders = self.mapped('sale_id')
            orders.update_effective_date()
        return res

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        for pick in self:
            if pick.date_done and pick.state == 'done':
                effective_date = datetime.strptime(pick.date_done, DEFAULT_SERVER_DATETIME_FORMAT)
                if pick.requested_date:
                    requested_date = datetime.strptime(pick.requested_date, DEFAULT_SERVER_DATE_FORMAT)
                    effective_date = requested_date
                pick.effective_date = effective_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return res

    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        inv_vals = super(StockPicking, self)._get_invoice_vals(key, inv_type, journal_id, move)
        sale = move.picking_id.sale_id
        if inv_type in ('out_invoice', 'out_refund'):
            if sale:
                inv_vals.update({
                    'supplier_cip': sale.supplier_cip,
                    })
            elif move.picking_id.partner_id:
                partner_id = move.picking_id.partner_id
                inv_vals.update({
                    'supplier_cip': partner_id.commercial_route_id.supplier_cip,
                    })
        return inv_vals


class StockMove(models.Model):
    _inherit = 'stock.move'

    supplier_id = fields.Many2one(
        string="Supplier",
        comodel_name='res.partner',
        related="picking_id.supplier_id",
        readonly=True, store=False, select=True)
    effective_date = fields.Date(
        string='Effective Date',
        related="picking_id.effective_date",
        readonly=True, store=True,
        help="Date on which the delivery order was delivered.")
