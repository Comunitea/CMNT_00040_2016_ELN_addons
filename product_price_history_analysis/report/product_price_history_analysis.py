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
from openerp import tools
from openerp import models, fields
from openerp.osv import osv

class ProductPriceHistoryAnalysis(models.Model):
    _name = 'product.price.history.analysis'
    _auto = False
    _rec_name = 'product_id'

    product_id = fields.Many2one(
        'product.product', string='Product', readonly=True)
    product_template_id = fields.Many2one(
        'product.template', string='Product Template', readonly=True)
    cost = fields.Float(string='Cost', group_operator='avg', readonly=True)
    datetime = fields.Datetime('Date', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company', readonly=True)

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
            """CREATE or REPLACE VIEW %s as (
            SELECT
                pph.id AS id,
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

class product_product(osv.osv):
    _inherit = "product.product"
        
    def action_view_history_analysis(self, cr, uid, ids, context=None):
        template_obj = self.pool.get("product.template")
        product_obj = self.pool.get("product.product")
        new_ids = ids
        for product in product_obj.browse(cr, uid, ids, context):
            bom = product.bom_ids and product.bom_ids[0] or False #Cogemos la primera
            if bom:
                for bom_line_id in bom.bom_line_ids:
                    new_ids.append(bom_line_id.product_id.id)
        templ_ids = list(set([x.product_tmpl_id.id for x in self.browse(cr, uid, new_ids, context=context)]))
        return template_obj.action_view_history_analysis(cr, uid, templ_ids, context=context)

class product_template(osv.osv):
    _inherit = 'product.template'
    
    def action_view_history_analysis(self, cr, uid, ids, context=None):
        value = {
            'domain': str([('product_template_id', 'in', ids)]),
            'context': "{'search_default_last_12_months':1}",
            'view_type': 'graph',
            'view_mode': 'graph',
            'res_model': 'product.price.history.analysis',
            'type': 'ir.actions.act_window',
            'nodestroy': True}
        return value
    
