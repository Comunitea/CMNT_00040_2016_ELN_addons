# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _



class WzdCancelStockPickingLine(models.TransientModel):
    _name="wzd.cancel.stock.picking.line"

    parent_id = fields.Many2one("wzd.sale.order.cancel")

    picking_id = fields.Integer("Id del albarán")
    name = fields.Char("Albarán")
    state = fields.Char("Estado")
    company = fields.Char("Compañia")



class WzdSaleOrderCancel(models.TransientModel):

    _name = 'wzd.sale.order.cancel'
    _description = 'Cancelar Orden de venta'



    orig_pick_ids = fields.Many2many('stock.picking', string="Albarán a cancelar")
    sale_ids = fields.Many2many('sale.order', string="Venta a cancelar")
    group_ids = fields.Many2many('procurement.order.order', string="Abastecimientos a cancelar")
    cancel_line_ids = fields.One2many('wzd.cancel.stock.picking.line', 'parent_id', string="Albaranes asociados")
    str = fields.Char("Cabecera")

    @api.model
    def default_get(self, fields):
        res = super(WzdSaleOrderCancel, self).default_get(fields)
        model = self._context.get('active_model', False)
        active_ids = self._context.get('active_ids')
        picking_ids= []
        lines = []
        if active_ids:
            if model == "sale.order":
                modelo ="Pedidos de venta"
                obj = self.sudo().env['sale.order'].browse(active_ids)
                picking_ids = obj.picking_ids
                res['sale_ids'] = [(6,0,obj.ids)]
            elif model == 'stock.picking':
                modelo = "Albaranes"
                obj = self.env['stock.picking'].browse(active_ids)
                group_ids = obj.mapped('group_id')
                picking_ids = self.sudo().env['stock.picking'].search([('group_id','in', group_ids.ids)])
                res['orig_pick_ids'] = [(6, 0, picking_ids.ids)]
            elif model == 'procurement.order':
                modelo = "Abastecimientos"
                obj = self.sudo().env['procurement.order'].browse(active_ids)
                group_ids = obj.mapped('group_id')
                picking_ids = self.sudo().env['stock.picking'].search([('group_id', 'in', group_ids.ids)])
                res['orig_pick_ids'] = [(6, 0, picking_ids.ids)]

        for pick in picking_ids:
            val = {'picking_id': pick.id,
                    'name': pick.name,
                    'state': pick.state,
                    'company': pick.company_id.name}
            lines.append(val)
            res['cancel_line_ids'] = lines

        if obj:
            str = "Albaranes de %s : %s" % (modelo, [x.name for x in obj])
            res['str'] = str
        return res

    @api.multi
    def cancel_all(self):
        domain = [('id','in', [x.picking_id for x in self.cancel_line_ids]), ('state', 'not in', ('cancel', 'done'))]
        picks_to_cancel = self.sudo().env['stock.picking'].search(domain)
        for pick in picks_to_cancel:
            pick.sudo(pick.get_pda_ic()).action_cancel()
        return {
            'name': 'Albaranes cancelados/',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'domain': [('id', '=', picks_to_cancel.ids)],
            'context': self.env.context}

