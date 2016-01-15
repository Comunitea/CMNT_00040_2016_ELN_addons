# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Omar Castiñeira Saavedra$ <omar@pexego.es>
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

class res_partner(osv.osv):

    _inherit = "res.partner"

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', select=1, required=True),
        'supplier_approved': fields.boolean('Supplier approved'),
        'supplier_type': fields.selection([('I','I'),('II','II'),('III','III')], string="Supplier type"),
        #'price_list': fields.one2many('product.supplierinfo', 'name', 'Price list')
    }


    def write(self, cr, uid, ids, vals, context=None):
        """Modificación del método de escritura de res.partner para que se
        produzca el cambio de la compañía en las direcciones del partner automáticamente
        al realizar el guardado de los datos del partner"""

        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]

        domain = []

        #Hacemos el cambio si ha cambiado la compañia
        if vals.get('company_id', False):
            for partner in self.browse(cr, uid, ids):
                if partner.address:
                    for address in partner.address:
                        address.write({'company_id': vals['company_id']})

        return super(res_partner, self).write(cr, uid, ids, vals, context=context)


res_partner()
