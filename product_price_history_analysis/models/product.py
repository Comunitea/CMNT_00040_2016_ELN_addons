# Copyright 2024 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, tools


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    def action_view_history_analysis(self):
        template_obj = self.env['product.template']
        product_obj = self.env['product.product']
        new_ids = ids
        new_products = self.env['product.product']
        for product in self:
            bom = product.bom_ids and product.bom_ids[0] or False # Cogemos la primera
            if bom:
                for bom_line_id in bom.bom_line_ids:
                    new_products |= bom_line_id.product_id
                    new_ids.append(bom_line_id.product_id.id)
        templ_ids = new_products.mapped('product_tmpl_id').ids
        return template_obj.action_view_history_analysis(templ_ids)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    @api.model
    def action_view_history_analysis(self, templ_ids):
        value = {
            'domain': str([('product_template_id', 'in', ids)]),
            'context': "{'search_default_last_12_months':1}",
            'view_type': 'graph',
            'view_mode': 'graph',
            'res_model': 'product.price.history.analysis',
            'type': 'ir.actions.act_window',
            'nodestroy': True}
        return value
