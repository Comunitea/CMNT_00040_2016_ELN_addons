# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta

class SaleOrderToWave(models.TransientModel):

    _name = 'sale.order.to.wave'
    _description = 'Add sale orders a picking wave'

    wave_id = fields.Many2one('stock.picking.wave', 'Picking Wave', required=True)

    @api.multi
    def attach_pickings(self):
        #use active_ids to add picking line to the selected wave

        wave_id = self.wave_id.id
        order_ids = self._context.get('active_ids', False)
        pick_ids = self.sudo().env['sale.order'].browse(order_ids).mapped('picking_ids')
        pick_ids.write({'wave_id': wave_id})


