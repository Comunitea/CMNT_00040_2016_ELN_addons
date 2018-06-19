# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from openerp import models, fields, api, exceptions, _

class SaleOrderCancelMulti(models.TransientModel):

    _name = 'sale.order.cancel.multi'

    @api.multi
    def cancel(self):
        obj_ids = self._context.get('active_ids', False)

        self._cr.execute( "select sl.id from stock_move sm " \
            
              "join procurement_order po on sm.procurement_id = po.id " \
              "join sale_order_line sol on sol.id = po.sale_line_id " \
              "join sale_order sl on sl.id = sol.order_id " \
              "where sm.state != 'done' and sm.invoice_state != 'invoiced' and sl.id in %s", (tuple(obj_ids),))
        records = self._cr.fetchall()

        sale_ids = self.env['sale.order'].browse([record[0] for record in records])
        print sale_ids
        for sale in sale_ids:
            try:
                sale.action_cancel()
            except:
                continue
        return {'type': 'ir.actions.act_window_close'}
