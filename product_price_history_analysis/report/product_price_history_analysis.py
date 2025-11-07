# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2016 QUIVAL, S.A. All Rights Reserved
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
from odoo import models, fields, api, tools


class ProductPriceHistoryAnalysis(models.Model):
    _name = 'product.price.history.analysis'
    _auto = False
    _rec_name = 'product_id'

    history_id = fields.Integer('id', readonly=True)
    product_id = fields.Many2one(
        'product.product', string='Product', readonly=True)
    product_template_id = fields.Many2one(
        'product.template', string='Product Template', readonly=True)
    cost = fields.Float(string='Cost', aggregator='avg', readonly=True)
    datetime = fields.Datetime('Date', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company', readonly=True)

    @api.model
    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute(
            """CREATE or REPLACE VIEW %s as (
            SELECT
                pph.id AS id,
                pph.id AS history_id,
                pph.product_template_id AS product_template_id,
                round(CAST(pph.cost as numeric), 3) AS cost,
                pph.datetime AS datetime,
                pph.company_id AS company_id,
                prod.id AS product_id
            FROM product_price_history AS pph
            JOIN product_product prod ON prod.product_tmpl_id = pph.product_template_id
            )"""
            % (self._table)
        )
