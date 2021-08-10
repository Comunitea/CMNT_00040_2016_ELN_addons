# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _
from datetime import datetime
from base64 import b64encode
from reportlab.lib import units
from reportlab.graphics import renderPM
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    packing_ids = fields.One2many(
        comodel_name='stock.picking.packing',
        inverse_name='picking_id',
        string='Packings')

    @api.multi
    def modify_picking_packing(self):
        c = self._context.copy()
        c.update(
            active_model=self._name,
            active_ids=self._ids,
            active_id=self._ids[0])
        spmp_obj = self.env['stock.picking.modify.packing'].with_context(c)
        created_id = spmp_obj.create({})
        return created_id.wizard_view()

    @api.multi
    def restore_picking_packing(self):
        res = self.packing_ids.unlink()
        return res

    @api.multi
    def action_print_gs1_128_label(self):
        p_dic = {}
        for picking in self:
            packing_ids = picking.get_packing_ids()
            for k, vals in packing_ids.items():
                pack_sscc = picking.get_sscc(k)
                if picking.id not in p_dic:
                    p_dic[picking.id] = []
                for val in vals:
                    pack_lot = val['lot_id']
                    pack_lot_name = val['lot_id'].name and pack_lot.name[:20] or '?'
                    try:
                        pack_date1 = datetime.strptime(pack_lot.use_date[:10], '%Y-%m-%d').strftime('%y%m%d')
                        pack_date2 = datetime.strptime(pack_lot.use_date[:10], '%Y-%m-%d').strftime('%d-%m-%Y')
                    except:
                        pack_date1 = '?'
                        pack_date2 = '?'
                    pack_dun14 = val['product_id'].dun14 or \
                        val['product_id'].ean13 and ('0' + val['product_id'].ean13) or '?'
                    pack_name = val['product_id'].name or '?'
                    pack_uos_qty = int(val['product_qty_uos'])
                    pack_uos_name = val['product_uos_id'].name or '?'
                    pack_qty_len = len(str(pack_uos_qty))
                    pack_qty_len = 0 if pack_qty_len%2==0 else 1 # 0: par, 1:impar - Usamos juego de caracteres C (num. dígitos par)
                    # \xf1 = FNC1 -> Sólo al principio o después de longitud variable si no es al final
                    codes = str('\xf1') + \
                            str('02') + str(pack_dun14) + \
                            str('15') + str(pack_date1) + \
                            str('37') + '0' * pack_qty_len + str(pack_uos_qty)
                    humanReadable1 = '(02)' + str(pack_dun14) + \
                                    '(15)' + str(pack_date1) + \
                                    '(37)' + '0' * pack_qty_len + str(pack_uos_qty)
                    pack_gs1_128_l1 = self.get_gs1_128_barcode_image(codes, width=2400, humanReadable=False)
                    codes = str('\xf1') + \
                            str('00') + pack_sscc + \
                            str('10') + str(pack_lot_name)
                    humanReadable2 = '(00)' + pack_sscc + \
                                    '(10)' + str(pack_lot_name)
                    pack_gs1_128_l2 = self.get_gs1_128_barcode_image(codes, width=2400, humanReadable=False)
                    p_dic[picking.id].append({
                        'product_pack': k,
                        'total_pack': len(packing_ids),
                        'pack_name': pack_name,
                        'pack_sscc': pack_sscc,
                        'pack_dun14': pack_dun14,
                        'pack_uos_qty': pack_uos_qty,
                        'pack_uos': pack_uos_name,
                        'pack_lot': pack_lot_name,
                        'pack_date': pack_date2,
                        'pack_gs1_128_l1': pack_gs1_128_l1,
                        'humanReadable1': humanReadable1,
                        'pack_gs1_128_l2': pack_gs1_128_l2,
                        'humanReadable2': humanReadable2,
                    })
        custom_data = {'lines_dic': p_dic}
        rep_name = 'stock_picking_packing.gs1_128_report_x1'
        if self._context.get('num_labels', 1) == 2:
            rep_name = 'stock_picking_packing.gs1_128_report_x2'
        rep_action = self.env['report'].get_action(self, rep_name)
        rep_action['data'] = custom_data
        return rep_action

    @api.multi
    def get_sscc(self, sequence=0):
        # Cálculo del código SSCC y el dígito de control
        # 18 dígitos con la siguiente estructura:
        # 1 dígito otorgado por la empresa (usaremos 1)
        # De 7 a 10 dígitos: parte fija. Prefijo GS1 de la empresa
        # De 6 a 9 dígitos: varía en función de la parte fija y es un número secuencial
        # 1 dígito: dígito de control
        self.ensure_one()
        gs1 = self.company_id.gs1
        if not gs1 or not gs1.isnumeric() or len(gs1) < 7 or len(gs1) > 10:
            raise exceptions.Warning(_("Warning!"),
                _("The company GS1 code is wrong"))
        pick_seq = str(sequence).encode('utf-8').decode('utf-8')
        if not pick_seq or not pick_seq.isnumeric():
            pick_seq = '00'
        sscc = '1' + gs1
        pick_num = str(self.id)
        i = (16 - 3) - len(pick_num + gs1)
        pick_num = pick_num[abs(i):] if i < 0 else u'0' * abs(i) + pick_num
        i = 3 - len(pick_seq)
        pick_seq = pick_seq[abs(i):] if i < 0 else u'0' * abs(i) + pick_seq
        sscc += pick_num + pick_seq
        # Cálculo del dígito de control
        pair_num = sum([int(sscc[i:i+1]) for i in range(len(sscc)) if (i+1)%2==0])
        odd_num = sum([int(sscc[i:i+1]) for i in range(len(sscc)) if (i+1)%2!=0])
        total_num = pair_num + odd_num * 3
        # Se busca el múltiplo de 10
        aux_num = total_num
        while aux_num % 10 != 0:
            aux_num += 1
        control = aux_num - total_num
        return str(sscc) + str(control)

    @api.model
    def get_gs1_128_barcode_image(self, value, width, barWidth=0.05*units.inch, fontSize=30, humanReadable=True):
        barcode = createBarcodeDrawing('Code128', value=value, barWidth=barWidth, fontSize=fontSize, humanReadable=humanReadable)
        drawing_width = width
        barcode_scale = drawing_width / barcode.width
        drawing_height = barcode.height * barcode_scale
        drawing = Drawing(drawing_width, drawing_height)
        drawing.scale(barcode_scale, barcode_scale)
        drawing.add(barcode, name='barcode')
        data = b64encode(renderPM.drawToString(drawing, fmt='PNG'))
        return data

    @api.multi
    def get_packing_ids(self):
        self.ensure_one()
        auto = self._context.get('auto', False)
        t_uom = self.env['product.uom']
        packing_ids = {}
        if self.packing_ids and not (auto in ('default', 'pallet', 'box')):
            line_ids = self.packing_ids.sorted(
                key=lambda a: (a.product_pack, a.product_id.default_code, a.lot_id))
            for line in line_ids:
                if line.product_pack not in packing_ids:
                    packing_ids[line.product_pack] = []
                product_qty_uos = t_uom._compute_qty(
                    line.product_uom_id.id, line.product_qty, line.product_uos_id.id)
                vals = {
                    'product_id': line.product_id,
                    'product_qty': line.product_qty,
                    'product_uom_id': line.product_uom_id,
                    'product_qty_uos': product_qty_uos,
                    'product_uos_id': line.product_uos_id,
                    'lot_id': line.lot_id,
                    'pack_ul_id': line.pack_ul_id,
                }
                packing_ids[line.product_pack].append(vals)
        else:
            line_ids = self.pack_operation_ids.filtered(lambda r: r.product_qty > 0.0)
            line_ids = line_ids.sorted(
                key=lambda a: (a.product_id.default_code, a.lot_id))
            k = 1
            packing_ids[1] = []
            for line in line_ids:
                product_uos_id = line.product_uom_id
                product_qty_uos = line.product_qty
                if line.linked_move_operation_ids:
                    move = line.linked_move_operation_ids[0].move_id
                    product_uos_id = move.product_uos or product_uos_id
                    product_qty_uos = t_uom._compute_qty(
                        line.product_uom_id.id, line.product_qty, product_uos_id.id)
                vals = {
                    'product_id': line.product_id,
                    'product_qty': line.product_qty, 
                    'product_uom_id': line.product_uom_id,
                    'product_qty_uos': product_qty_uos, 
                    'product_uos_id': product_uos_id,
                    'lot_id': line.lot_id,
                    'pack_ul_id': False,
                }
                if auto in ('pallet', 'box'):
                    boxes_pallet = 1
                    if auto == 'pallet':
                        pls_ids = line.product_id.product_logistic_sheet_ids
                        boxes_pallet = pls_ids and pls_ids[0].pallet_boxes_pallet or 1
                    if auto == 'box':
                        boxes_pallet = 1
                    units_pallet = t_uom._compute_qty(
                        product_uos_id.id, boxes_pallet, line.product_uom_id.id) or line.product_qty
                    boxes_pallet = t_uom._compute_qty(
                        line.product_uom_id.id, units_pallet, product_uos_id.id)
                    split = True if line.product_qty%units_pallet == 0 else False
                    if split:
                        total_pallets = int(line.product_qty / units_pallet) or 1
                        vals['product_qty'] = units_pallet
                        vals['product_qty_uos'] = boxes_pallet
                        for i in range(total_pallets):
                            packing_ids[k] = [vals]
                            k += 1
                    else:
                        packing_ids[k] = [vals]
                        k += 1
                else: # default
                    packing_ids[1].append(vals)
        return packing_ids
