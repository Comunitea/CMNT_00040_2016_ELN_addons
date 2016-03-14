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
from openerp.osv import orm, fields


class stock_move(orm.Model):
    _inherit = 'stock.move'
    _columns = {
        'reworked': fields.boolean('Reworked')
    }

    def action_scrap(self, cr, uid, ids, quantity, location_id, restrict_lot_id=False, restrict_partner_id=False, context=None):
        res = super(stock_move, self).action_scrap(cr, uid, ids, quantity, location_id,  restrict_lot_id=restrict_lot_id, restrict_partner_id=restrict_partner_id, context=context)

        is_reworks_location = self.pool.get('stock.location').browse(cr, uid, location_id, context=context).reworks_location
        
        for move in self.browse(cr, uid, ids):
            if is_reworks_location:
                self.pool.get('stock.move').write(cr, uid, res, {'reworked': True})
        return res


class stock_production_lot(orm.Model):
    _inherit = 'stock.production.lot'
    _columns = {
        'recovery': fields.boolean('Recovery')
    }


class stock_location(orm.Model):
    _inherit = 'stock.location'
    _columns = {
        'reworks_location': fields.boolean('Reworks location', help='Check this box to generate reworks when create a scrap move to this location. Should also mark the check box "Scrap Location".')
    }
