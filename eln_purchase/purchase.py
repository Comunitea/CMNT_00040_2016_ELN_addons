# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.osv import orm, fields


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    def _get_products_names(self, cr, uid, ids, field_name, args, context=None):
        if context is None:
            context = {}
        res = {}

        lang = ('lang' in context and context['lang'])

        for cur_obj in self.browse(cr, uid, ids, context={'lang':lang}):
            stream = []
            res[cur_obj.id] = "[]"
            if cur_obj.order_line:
                for line in cur_obj.order_line:
                    if line.product_id and line.product_id.name:
                        stream.append(line.product_id.name)
                res[cur_obj.id] = u" ###, ".join(stream)

        return res

    _columns = {
        'lines_product_name_str': fields.function(_get_products_names, method=True, string='Lines', type='char', size=255, readonly=True),
        'container_numbers': fields.char('Container numbers', size=32, help="Container numbers assigned to the order.", readonly=False, states={'done': [('readonly', True)],'cancel': [('readonly', True)]}),
    }
    _defaults = {
        'invoice_method': 'picking',
    }


class procurement_order(orm.Model):
    _inherit = 'procurement.order'

    def _calc_new_qty_price(self, cr, uid, procurement, po_line=None, cancel=False, context=None):
        res = super(procurement_order, self)._calc_new_qty_price(cr, uid, procurement, po_line=po_line, cancel=cancel, context=context)
        # En la función original cuando se llama a price_get no se tiene en cuenta la compañía del abastecimiento,
        # y cuando es llamada desde planificadores usa la del usuario (generalmente admin) lo cual es un error en caso de multicompañía
        if res:
            qty = res[0]
            price = po_line.price_unit
            if qty != po_line.product_qty:
                pricelist_obj = self.pool.get('product.pricelist')
                pricelist_id = po_line.order_id.partner_id.property_product_pricelist_purchase.id
                ctx_company = dict(context or {}, force_company=procurement.company_id.id)
                uom_id = procurement.product_id.uom_po_id.id
                price = pricelist_obj.price_get(cr, uid, [pricelist_id], procurement.product_id.id, qty, po_line.order_id.partner_id.id, dict(ctx_company, uom=uom_id))[pricelist_id]
            res = qty, price
        return res
