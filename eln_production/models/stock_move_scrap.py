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
from openerp import models, api, exceptions, _


class StockMoveScrap(models.TransientModel):
    _inherit = 'stock.move.scrap'

    @api.model
    def default_get(self, fields):
        res = super(StockMoveScrap, self).default_get(fields)
        move_obj = self.env['stock.move']
        move_id = move_obj.browse(self._context.get('active_id', False))
        if ('restrict_lot_id' in fields) and move_id.restrict_lot_id:
            res.update({'restrict_lot_id': move_id.restrict_lot_id.id})
        return res

    @api.multi
    def move_scrap(self):
        move_obj = self.env['stock.move']
        move_ids = move_obj.browse(self._context.get('active_ids', False))
        for data in self:
            if not data.restrict_lot_id and \
                (data.product_id.track_production or data.product_id.track_all):
                raise exceptions.Warning(
                    _('Warning!'),
                    _('You must assign a serial number for the product %s') % (data.product_id.name))
            if data.restrict_lot_id:
                move_ids.write({'restrict_lot_id': data.restrict_lot_id.id})
        res = super(StockMoveScrap, self).move_scrap()
        return res
