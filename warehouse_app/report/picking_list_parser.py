# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class PickingListParser(models.AbstractModel):

    """
    """
    _name = 'report.warehouse_app.picking_list_report'


    @api.multi
    def get_docargs(self, ids, model):

        objs = self.env[model].browse(ids)
        picks = []
        for obj in objs:
            pick = {'name': obj.name, 'state': obj.state, 'user_id': obj.user_id and obj.user_id.name}
            if model == 'stock.picking':
                ops_obj = obj.pack_operation_ids
            else:
                ops_obj = obj.pack_operation_ids
            docs = []
            ops = []
            for op in ops_obj:
                val = {'name': op.product_id.display_name,
                       'barcode': op.product_id.ean13,
                       'lot': op.lot_id.name,
                       'location_id_name': op.location_id.display_name,
                       'location_id_barcode': op.location_id.loc_barcode,
                       'location_dest_id_name': op.location_dest_id.display_name,
                       'location_dest_id_barcode': op.location_dest_id.loc_barcode,
                       'qty': u'%s %s'%(op.product_qty, op.product_uom_id)
                       }
                ops.append(val)
            pick['ops'] = ops
            picks.append(pick)
        docargs = {
            'doc_ids': [],
            'doc_model': 'stock.picking',
            'docs': objs,

        }
        return docargs

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report_name = 'warehouse_app.picking_list_report'
        model = 'stock.picking'
        objs = self.env[model].browse(self.ids)
        docargs = {
            'doc_ids': [],
            'doc_model': 'stock.picking',
            'docs': objs,
        }
        docargs = self.get_docargs(self.ids, model)
        return report_obj.render(report_name, docargs)
