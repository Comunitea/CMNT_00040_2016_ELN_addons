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
from osv import osv, fields

class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    def _get_cod_product_supplier(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        for line in self.browse(cr, uid, ids):

            res[line.id] = u''
            if line.product_id and line.product_id.seller_ids:
                if line.product_id.seller_ids[0].product_code:
                    res[line.id] = line.product_id.seller_ids[0].product_code
        #print res
        return res

    _columns = {
        'supplier': fields.function(_get_cod_product_supplier, string='Cod. Supplier', type='char')
    }
purchase_order_line()

class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    def _get_invoice_address(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        partner_obj = self.pool.get('res.partner')
        res = {}
        for order in self.browse(cr, uid, ids):
            res[order.id] = {'invoice_name': '',  'invoice_address': '',
                             'invoice_address2': '', 'invoice_zip': '',
                             'invoice_city': '', 'invoice_prov': '',
                             'invoice_state': '', 'invoice_phone': '',
                             'invoice_email': '', 'invoice_fax': '','invoice_vat': ''}
            address_id = partner_obj.address_get(cr, uid, [order.partner_id.id], ['invoice'])['invoice']
            if address_id:
                add = self.pool.get('res.partner.address').browse(cr, uid, address_id)
                res[order.id] = {'invoice_name': add.partner_id.name,
                                 'invoice_address': add.street,
                                 'invoice_address2': add.street2,
                                 'invoice_zip': add.zip,
                                 'invoice_city': add.city,
                                 'invoice_prov': add.state_id.name,
                                 'invoice_state': add.country_id.name,
                                 'invoice_phone': add.phone,
                                 'invoice_email': add.email,
                                 'invoice_fax': add.fax,
                                 'invoice_vat': add.partner_id.vat}
        #print res
        return res
 
    _columns = {
	    'invoice_name': fields.function(_get_invoice_address, type='char', string='Invoice name', multi='address'),
        'invoice_address': fields.function(_get_invoice_address, type='char', string='Invoice address', multi='address'),
        'invoice_address2': fields.function(_get_invoice_address, type='char', string='Invoice address2', multi='address'),
        'invoice_zip': fields.function(_get_invoice_address, type='char', string='Invoice zip', multi='address'),
        'invoice_city': fields.function(_get_invoice_address, type='char', string='Invoice city', multi='address'),
        'invoice_prov': fields.function(_get_invoice_address, type='char', string='Invoice prov', multi='address'),
        'invoice_state': fields.function(_get_invoice_address, type='char', string='Invoice state', multi='address'),
        'invoice_phone': fields.function(_get_invoice_address, type='char', string='Invoice phone', multi='address'),
        'invoice_fax': fields.function(_get_invoice_address, type='char', string='Invoice fax', multi='address'),
        'invoice_email': fields.function(_get_invoice_address, type='char', string='Invoice email', multi='address'),
        'invoice_vat': fields.function(_get_invoice_address, type='char', string='Invoice vat', multi='address'),
	}
purchase_order()


