# -*- coding: utf-8 -*-
# Copyright 2024 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sii_operation_date = fields.Date(
        string='SII operation date', copy=False,
        help="Indicates the operation date. If it is a refund invoice that "
             "refers to several transaction dates, the last day of the natural "
             "month in which the transaction documented by the most recent "
             "amended invoice (the one with the latest date) was carried out "
             "will be recorded.")

    @api.multi
    def _get_sii_invoice_dict_out(self, cancel=False):
        """
        Hay casos en los que debemos informar de la FechaOperacion.
        Por ejemplo cuando vamos a enviar una factura emitida (normalmente
        rectificativa, como un rappel, etc.) con un tipo de impuesto existente
        en un periodo anterior al actual y que ya no está vigente. 
        Se debe en ese caso registrar la fecha de la operación. Cuando
        la factura rectificada afecte a muchas facturas, se pondrá el último día
        del mes del último periodo afectado. 

        """
        res = super(AccountInvoice, self)._get_sii_invoice_dict_out(
            cancel=cancel,
        )
        operation_date = (
            self.sii_operation_date and
            self.sii_operation_date < self.date_invoice and
            self._change_date_format(self.sii_operation_date)
        )
        if not cancel and res.get('FacturaExpedida') and operation_date:
            if not 'FechaOperacion' in res['FacturaExpedida']:
                res['FacturaExpedida']['FechaOperacion'] = operation_date
        return res
