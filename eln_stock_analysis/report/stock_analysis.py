# -*- coding: utf-8 -*-
# © 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import tools
from openerp import models, fields
import openerp.addons.decimal_precision as dp


class StockAnalysis(models.Model):
    _inherit = 'stock.analysis'

    use_date = fields.Datetime('Best before Date', readonly=True)
    cost = fields.Float('Cost', digits=dp.get_precision('Product Price'), readonly=True)

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
            """CREATE or REPLACE VIEW %s as (
            SELECT
                quant.id AS id,
                quant.product_id AS product_id,
                quant.location_id AS location_id,
                quant.qty AS qty,
                quant.lot_id AS lot_id,
                quant.package_id AS package_id,
                quant.in_date AS in_date,
                quant.company_id,
                template.categ_id AS categ_id,
                spl.use_date AS use_date,
                (quant.cost * quant.qty) AS cost
            FROM stock_quant AS quant
            JOIN product_product prod ON prod.id = quant.product_id
            JOIN product_template template
                ON template.id = prod.product_tmpl_id
            LEFT JOIN stock_production_lot AS spl ON spl.id = quant.lot_id
            )"""
            % (self._table)
        )
