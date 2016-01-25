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

class stock_picking(orm.Model):
    _inherit = 'stock.picking'
    _columns = {
        'supplier_id': fields.many2one('res.partner', 'Supplier', readonly=True,domain = [('supplier','=',True)],states={'draft': [('readonly', False)]}, select=True),
        'carrier_id': fields.many2one('res.partner', 'Carrier', readonly=True, states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)], 'assigned': [('readonly', False)]}, select=True),
        'commitment_date': fields.related('sale_id', 'commitment_date', type='date', string="Commitment Date", readonly=True, 
                           help="Date on which delivery of products is to be made."),
        'supplier_cip': fields.related('sale_id', 'supplier_cip', type='char', string="CIP", readonly=True,  
                           help="Código interno del proveedor."),
    }

    def _prepare_invoice_group(self, cr, uid, picking, partner, invoice, context=None):
        """ Builds the dict for grouped invoices
            @param picking: picking object
            @param partner: object of the partner to invoice (not used here, but may be usefull if this function is inherited)
            @param invoice: object of the invoice that we are updating
            @return: dict that will be used to update the invoice
        """
        """ Modificamos la función para que si no se le pasa fecha en el asistente de facturación en lugar
            de generar la factura borrador sin fecha que la genere con la fecha real del albarán.
            Al ser factura resumen en este caso, se utiliza la fecha más reciente de todos los albaranes.
        """
        res = super(stock_picking, self)._prepare_invoice_group(cr, uid, picking, partner, invoice, context)

        if not context.get('date_inv', False):
            if picking and picking.date_done:
                if invoice.date_invoice < picking.date_done:
                    res.update({'date_invoice': picking.date_done})

        return res

    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        """ Builds the dict containing the values for the invoice
            @param picking: picking object
            @param partner: object of the partner to invoice
            @param inv_type: type of the invoice ('out_invoice', 'in_invoice', ...)
            @param journal_id: ID of the accounting journal
            @return: dict that will be used to create the invoice object
        """
        """ Modificamos la función para que si no se le pasa fecha en el asistente de facturación en lugar
            de generar la factura borrador sin fecha que la genere con la fecha real del albarán.
        """
        res = super(stock_picking, self)._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context)

        if not context.get('date_inv', False):
            if picking and picking.date_done:
                res.update({'date_invoice': picking.date_done})

        return res


class stock_move(orm.Model):
    _inherit = 'stock.move'
    _columns = {
        'supplier_id': fields.many2one('res.partner', 'Supplier', readonly=True,domain = [('supplier','=',True)],states={'draft': [('readonly', False)]}, select=True)
    }

