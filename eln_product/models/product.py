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
import math

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


def dun_checksum(eancode):
    """returns the checksum of an dun string of length 14, returns -1 if the string has the wrong length"""
    if len(eancode) != 14:
        return -1
    oddsum=0
    evensum=0
    total=0
    eanvalue=eancode
    reversevalue = eanvalue[::-1]
    finalean=reversevalue[1:]

    for i in range(len(finalean)):
        if i % 2 == 0:
            oddsum += int(finalean[i])
        else:
            evensum += int(finalean[i])
    total=(oddsum * 3) + evensum

    check = int(10 - math.ceil(total % 10.0)) %10
    return check

def check_dun(eancode):
    """returns True if eancode is a valid dun14 string, or null"""
    if not eancode:
        return True
    if len(eancode) != 14:
        return False
    try:
        int(eancode)
    except:
        return False
    return dun_checksum(eancode) == int(eancode[-1])


class ProductProduct(models.Model):
    _inherit = 'product.product'

    partner_product_code = fields.Char('Partner code', size=64)
    dun14 = fields.Char('DUN14', size=14)
    development_code = fields.Char('Development code', size=64)
    qty_dispo = fields.Float(
        string='Stock available',
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_product_dispo',
        help="Stock available for assignment. It refers to the actual stock not reserved.")
    ramp_up_date = fields.Date('Ramp Up Date', copy=False,
        default=lambda s: fields.Date.context_today(s))

    @api.multi
    def _check_dun_key(self):
        for product in self:
            if not check_dun(product.dun14):
                return False
        return True

    _constraints = [(_check_dun_key, 'You provided an invalid "DUN14 Barcode" reference.', ['dun14'])]

    @api.multi
    def _product_dispo(self):
        for product in self:
            qty_dispo = product.qty_available - product.outgoing_qty
            product.qty_dispo = qty_dispo if qty_dispo > 0.0 else 0.0

    @api.onchange('ean13')
    def onchange_ean13(self):
        """
            Comprueba que no esté en uso ya el código ean introducido. Si lo está muestra un aviso
        """
        if self.ean13:
            product_ids = self.search([('ean13', '=', self.ean13), ('id', '!=', self._origin.id), ('active', '=', True)], limit=100)
            if product_ids:
                cadena = '| '
                for product_id in product_ids:
                    cadena += product_id.default_code + ' | '
                warning = {
                    'title': _('Warning!'),
                    'message' : _('The EAN-13 code you entered is already in use.\nThe references of related products are: %s') % (cadena)
                }
                return {'warning': warning}

    @api.onchange('dun14')
    def onchange_dun14(self):
        """
            Comprueba que no esté en uso ya el código dun introducido. Si lo está muestra un aviso
        """
        if self.dun14:
            product_ids = self.search([('dun14', '=', self.dun14), ('id', '!=', self._origin.id), ('active', '=', True)], limit=100)
            if product_ids:
                cadena = '| '
                for product_id in product_ids:
                    cadena += product_id.default_code + ' | '
                warning = {
                    'title': _('Warning!'),
                    'message' : _('The DUN-14 code you entered is already in use.\nThe references of related products are: %s') % (cadena)
                }
                return {'warning': warning}

    @api.onchange('state')
    def onchange_state(self):
        if self.state == 'draft':
            self.ramp_up_date = False
        elif self.state == 'sellable' and self.ramp_up_date == False:
            self.ramp_up_date = fields.Date.context_today(self)



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    uos_coeff = fields.Float(digits=(16,10))

