# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Comunitea All Rights Reserved
#    $Jesús Ventosinos Mayor <jesus@comunitea.com>$
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
from openerp import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    picking_count = fields.Integer('Deliveries',
        compute='_get_deliveries_count')
    out_picking_ids = fields.One2many(
        comodel_name='stock.picking',
        inverse_name='partner_id',
        domain=[('picking_type_id.code', '=', 'outgoing')],
        string='Pickings'
    )

    @api.multi
    def _get_deliveries_count(self):
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing')])
        for partner in self:
            domain = [
                ('partner_id', '=', partner.id),
                ('picking_type_id', 'in', picking_type.ids),
            ]
            picking_count = self.env['stock.picking'].search(domain, count=True)
            partner.picking_count = picking_count

    @api.multi
    def action_picking_out(self):
        picking_type_obj = self.env['stock.picking.type']
        picking_type = picking_type_obj.search([('code', '=', 'outgoing')])
        domain = [
            ('partner_id', '=', self.id),
            ('picking_type_id', 'in', picking_type.ids)
        ]
        return {
            'domain': domain,
            'name': _('Pickings'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': {},
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
        }
