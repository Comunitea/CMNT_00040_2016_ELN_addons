# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class LocationTagParser(models.AbstractModel):
    """
    """
    _name = 'report.warehouse_app.location_tag_report'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        location_onj = self.env['stock.location']
        report_name = 'warehouse_app.location_tag_report'
        if not data:
            return
        location = location_onj.browse(data['location_id'])
        vals = {'prueba': 'Hola prueba'}

        docargs = {
            'doc_ids': [],
            'doc_model': 'stock.location',
            'docs': location,
            'vals': vals,
        }
        return report_obj.render(report_name, docargs)
