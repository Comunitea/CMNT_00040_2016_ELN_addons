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
from openerp import models, fields, api, exceptions, _
from openerp import netsvc


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    merged_into_id = fields.Many2one('mrp.production', 'Merged into', required=False, readonly=True,
        help='Production order in which this production order has been merged into.')
    product_ingredient_ids = fields.One2many('mrp.production', 'merged_into_id', string='Merged from',
        help='List of production orders that have been merged into the current one.')

    @api.multi
    def _do_merge(self, invalid_ids=[]):
        self.ensure_one()
        if self.id in invalid_ids:
            invalid_ids.remove(self.id)
        if not invalid_ids:
            raise exceptions.except_orm(
                _('Error !'),
                _('To merge at least two productions are needed.'))
        if self.state not in ('confirmed','ready'):
            raise exceptions.except_orm(
                _('Error !'),
                _('Production order "%s" must be in status "confirmed" or "ready".') % self.name)
        product_qty = self.product_qty
        priority = self.priority

        for production in self.env['mrp.production'].browse(invalid_ids):
            if production.state not in ('confirmed', 'ready'):
                raise exceptions.except_orm(
                    _('Error !'),
                    _('Production order "%s" must be in status "confirmed" or "ready".') % production.name)
            if production.product_id != self.product_id:
                raise exceptions.except_orm(
                    _('Error !'),
                    _('Production order "%s" product is different from the one in the first selected order.') % production.name)
            if production.product_uom != self.product_uom:
                raise exceptions.except_orm(
                    _('Error !'),
                    _('Production order "%s" UOM is different from the one in the first selected order.') % production.name)
            if production.bom_id != self.bom_id:
                raise exceptions.except_orm(
                    _('Error !'),
                    _('Production order "%s" BOM is different from the one in the first selected order.') % production.name)
            if production.routing_id != self.routing_id:
                raise exceptions.except_orm(
                    _('Error !'),
                    _('Production order "%s" routing is different from the one in the first selected order. %s - %s') % (production.name, production.routing_id.name, self.routing_id.name))
            if production.product_uos != self.product_uos:
                raise exceptions.except_orm(
                    _('Error !'),
                    _('Production order "%s" UOS is different from the one in the first selected order.') % production.name)
            product_qty += production.product_qty
            if production.priority > priority:
                priority = production.priority

        self.write({
            'merged_into_id': self.id,
            'priority': priority,
        })

        wf_service = netsvc.LocalService("workflow")

        # Cancel 'old' productions
        for invalid_id in invalid_ids:
            wf_service.trg_validate(self.env.uid, 'mrp.production', invalid_id, 'button_cancel', self.env.cr)

        wizard = self.env['change.production.qty'].with_context(active_id=self.id).create({'product_qty': product_qty})
        wizard.change_prod_qty()

        return self.id

