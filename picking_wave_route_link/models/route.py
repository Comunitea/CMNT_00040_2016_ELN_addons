# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields


class Route(models.Model):
    _inherit = "route"

    ir_sequence_id = fields.Many2one('ir.sequence', string="Sequencia", help="Secuencia para las agrupaciones de esta ruta", domain="[('code','=','picking_wave_route_link')]")
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking type', help='Picking type for outgoing pickings')

