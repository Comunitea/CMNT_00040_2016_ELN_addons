# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, api


class ProductTagParser(models.AbstractModel):
    """
    """
    _name = 'report.warehouse_app.product_tag_report'

   
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        pick_obj = self.env['product.product']
        report_name = 'warehouse_app.product_tag_report'
        if not data:
            return
        product = pick_obj.browse(data['product_id'])
        vals = {'prueba': 'Hola prueba'}

        docargs = {
            'doc_ids': [],
            'doc_model': 'product.product',
            'docs': product,
            'vals': vals,
        }
        return report_obj.render(report_name, docargs)


class LotTagParser(models.AbstractModel):
    """
    """
    _name = 'report.warehouse_app.production_lot_tag_report'

   
    def render_html(self, data=None):
        report_obj = self.env['report']
        report_name = 'warehouse_app.production_lot_tag_report'
        vals = {'prueba': 'Hola prueba'}

        docargs = {
            'doc_ids': [],
            'doc_model': 'stock.production.lot',
            'docs': self.sudo().env['stock.production.lot'].browse(self.ids),
            'vals': vals,
        }
        return report_obj.render(report_name, docargs)
