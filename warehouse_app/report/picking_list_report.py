# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class PickingListReport(models.AbstractModel):
    """
    """
    _name = 'report.warehouse_app.picking_list_report'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report_name = 'warehouse_app.picking_list_report'
        docargs = {
            'doc_ids': self.sudo().ids,
            'doc_model': 'stock.picking',
            'docs': self.sudo().env['stock.picking'].browse(self.sudo().ids),
        }
        return report_obj.render(report_name, docargs)


class WavePickingListReport(models.AbstractModel):
    """
    """
    _name = 'report.warehouse_app.wave_picking_list_report'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report_name = 'warehouse_app.wave_picking_list_report'
        docargs = {
            'doc_ids': self.sudo().ids,
            'doc_model': 'stock.picking.wave',
            'docs': self.sudo().env['stock.picking.wave'].browse(self.sudo().ids),
        }
        return report_obj.render(report_name, docargs)
