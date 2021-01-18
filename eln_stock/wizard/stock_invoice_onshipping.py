# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2017 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp import models, fields, api, exceptions, _


class StockInvoiceOnshipping(models.TransientModel):
    _inherit = 'stock.invoice.onshipping'

    @api.model
    def view_init(self, fields_list):
        active_ids = self.env.context.get('active_ids', [])
        domain = [
            ('id', 'in', active_ids),
            ('state', '!=', 'done')
        ]
        invalid_ids = self.env['stock.picking'].search(domain)
        if invalid_ids:
            raise exceptions.Warning(
                _("Warning!"),
                _("At least one of the selected picking lists are not in 'done' state and cannot be invoiced."))
        return super(StockInvoiceOnshipping, self).view_init(fields_list)

    @api.model
    def _get_journal(self):
        res = super(StockInvoiceOnshipping, self)._get_journal()
        if res and 'sii_simplified_invoice' in self.env['res.partner']._fields:
            res_ids = self.env.context.get('active_ids', [])
            picking_ids = self.env['stock.picking'].browse(res_ids)
            sii_enabled = picking_ids[0].company_id.sii_enabled
            if sii_enabled:
                simplified_invoice = picking_ids.mapped(
                    'partner_id.commercial_partner_id.sii_simplified_invoice')
                if simplified_invoice and not all(simplified_invoice) and any(simplified_invoice):
                    raise exceptions.Warning(
                        _("Warning!"),
                        _("It is not allowed to create ordinary invoices and simplified invoices at the same time."))
                if simplified_invoice and all(simplified_invoice):
                    aj_obj = self.env['account.journal']
                    journal_id = aj_obj.browse(res)
                    domain = [
                        ('type', '=', journal_id.type),
                        ('name', 'ilike', 'simplifi'),
                    ]
                    new_journal_id = aj_obj.search(domain, limit=1)
                    if not new_journal_id:
                        raise exceptions.Warning(
                            _("Warning!"),
                            _("A valid journal was not found for simplified invoices."))
                    res = new_journal_id.id
        return res

    journal_id = fields.Many2one(default=_get_journal)
