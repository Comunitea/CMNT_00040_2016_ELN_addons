# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Omar Castiñeira Saavedra$ <omar@pexego.es>
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
from openerp import models, api, fields, _


class res_partner(models.Model):
    _inherit = "res.partner"

    company_id = fields.Many2one(required=True)
    supplier_approved = fields.Boolean('Supplier approved')
    supplier_type = fields.Selection([
        ('I', 'I'), 
        ('II', 'II'), 
        ('III', 'III'), 
        ], string="Supplier type")
    route_id = fields.Many2one('route', 'Route')
    customer_state = fields.Selection([
        ('active', 'Active'), 
        ('inactive_closed', 'Inactive (closed)'), 
        ('inactive_unpaid', 'Inactive (unpaid)'), 
        ('inactive_new_vat', 'Inactive (new vat)')
        ], string="Customer state", default='active')

    @api.model
    def create(self, vals):
        if vals.get('parent_id', False) and not vals.get('company_id', False):
            partner = self.browse(vals['parent_id'])
            vals['company_id'] = partner.company_id.id
        return super(res_partner, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('company_id', False):
            for partner in self:
                if partner.child_ids:
                    partner.child_ids.write({'company_id': vals['company_id']})
        return super(res_partner, self).write(vals)

    @api.multi
    def onchange_address(self, use_parent_address, parent_id):
        res = super(res_partner, self).onchange_address(use_parent_address, parent_id)
        if parent_id:
            parent = self.browse(parent_id)
            if 'value' not in res:
                res['value'] = {}
            res['value']['company_id'] = parent.company_id.id
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.parent_id:
            if self.company_id and self.parent_id.company_id != self.company_id:
                self.company_id = self.parent_id.company_id
                warning = {
                    'title': _('Warning!'),
                    'message' : _('You can not change the company of the address. It must be the same as the company of the partner to which it belongs.')
                            }
                return {'warning': warning}
