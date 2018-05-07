# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields

from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare, float_round


class StockMoveCOnsume(models.TransientModel):
    _inherit = "stock.move.consume"

    package_ids = fields.Many2many('stock.quant.package')
    restrict_package_id = fields.Many2one('stock.quant.package', "Package")
    move_id = fields.Many2one('stock.move')

    @api.model
    def default_get(self, fields):
        res = super(StockMoveCOnsume, self).default_get(fields)
        move = self.env['stock.move'].browse(self._context.get('active_id'))
        quant_id = self.env['stock.quant'].search([('reservation_id','=', move.id)])
        lot_id = False
        package_id = False
        if quant_id:
            lot_id = quant_id.lot_id and quant_id.lot_id.id or False
            package_id = quant_id.package_id and quant_id.package_id.id or False
        #domain = [('product_id', '=', res['product_id']), ('package_id', '!=', False)]
        #package_ids = self.env['stock.quant'].search_read(domain, ['package_id'])
        #package_ids = [x['package_id'][0] for x in package_ids]
        res.update({'restrict_lot_id': lot_id or move.restrict_lot_id and move.restrict_lot_id.id or False,
                    'move_id': move and move.id,
                    #'package_ids': [(6, 0, package_ids)],
                    'restrict_package_id': package_id or move.restrict_package_id and move.restrict_package_id.id or False})
        return res

    @api.onchange('restrict_package_id')
    def onchange_restrict_package_id(self):
        if self.restrict_package_id:
            self.location_id = self.restrict_package_id.location_id
            self.restrict_lot_id = self.restrict_package_id.lot_id


    @api.onchange('product_id')
    def onchange_product_id(self):

        domain = [('product_id', '=', self.product_id.id), ('package_id', '!=', False)]
        package_ids = self.env['stock.quant'].search_read(domain, ['package_id'])
        package_ids = [x['package_id'][0] for x in package_ids]
        return {'domain': {'restrict_package_id': [('id', 'in', [package_ids])]}}