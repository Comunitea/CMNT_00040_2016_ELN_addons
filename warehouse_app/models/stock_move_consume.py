# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields

from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare, float_round


class StockMoveCOnsume(models.TransientModel):
    _inherit = "stock.move.consume"


    def get_package(self):
        return
        import ipdb; ipdb.set_trace()
        move = self.env['stock.move'].browse(self._context.get('active_id'))
        product_id = move.product_id
        package = self.env['stock.quant.package'].search([]).filtered(lambda x:x.product_id == product_id)
        self.package_ids = [(6,0, package.ids)]


    package_ids = fields.One2many('stock.quant.package', compute="get_package")
    restrict_package_id = fields.Many2one('stock.quant.package', "Package")
    move_id = fields.Many2one('stock.move')

    @api.model
    def default_get(self, fields):

        res = super(StockMoveCOnsume, self).default_get(fields)
        move = self.env['stock.move'].browse(self._context.get('active_id'))
        package = self.env['stock.quant.package'].search([]).filtered(lambda x: x.product_id.id == res['product_id'])
        res.update({'restrict_lot_id': move.restrict_lot_id and move.restrict_lot_id.id or False,
                    'move_id': move and move.id,
                    'package_ids': [(6,0,package.ids)],
                    'restrict_package_id': move.restrict_package_id and move.restrict_package_id.id or False})
        print res
        return res


    @api.onchange('restrict_package_id')
    def onchange_restrict_package_id(self):
        if self.restrict_package_id:
            self.location_id = self.restrict_package_id.location_id
            self.restrict_lot_id = self.restrict_package_id.lot_id
