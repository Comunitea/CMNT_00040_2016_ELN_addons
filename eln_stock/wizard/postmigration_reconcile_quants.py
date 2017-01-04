# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp import models, api

class postmigration_reconcile_quants(models.TransientModel):
    _name = 'postmigration.reconcile.quants'

    @api.multi
    def reconcile_quants(self):
        t_move = self.env["stock.move"]
        #stock_warehouses = []
        #for wh in self.env['stock.warehouse'].search([]):
        #    if wh.wh_input_stock_loc_id:
        #        stock_warehouses.append(wh.wh_input_stock_loc_id.id)
        user_company_ids = self.env['res.users'].browse(self._uid).company_id
        user_company_ids += user_company_ids.child_ids
        company_ids = [x.id for x in user_company_ids]
        domain = [('state', '=', 'done'),
                  #('location_dest_id', 'in', stock_warehouses),
                  ('location_id.usage', '!=', 'internal'),
                  ('company_id', 'in', company_ids),
        ]
        move_objs = t_move.search(domain, order='date')
        count = 1
        len_move = len(move_objs)
        for move in move_objs:
            print("RECONCILIANDO MOVIMIENTO            %s de %s" % (count, len_move))
            for quant in move.quant_ids:
                if quant.location_id.id == move.location_dest_id.id:  #To avoid we take a quant that was reconcile already
                    print("RECONCILIANDO QUANTS DEL MOVIMIENTO %s" % count)
                    self.env['stock.quant']._quant_reconcile_negative(quant, move)
            count += 1
        return True
       
