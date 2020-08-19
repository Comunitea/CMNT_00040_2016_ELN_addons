# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos All Rights Reserved
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

from openerp import models, fields, api


class CancelMaintenanceRequestWizard(models.TransientModel):
    _name = "cancel.maintenance.request.wizard"

    reason = fields.Text('Reason for cancellation',
        required=True)

    @api.multi
    def close_confirm(self):
        self.ensure_one()
        record_id = self._context.get('active_id', False)
        assert record_id, _('Active Id not found')
        request_id = self.env['maintenance.request'].browse(record_id)
        request_id.write({'state': 'cancel', 'cancel_reason' : self.reason})
        return {'type': 'ir.actions.act_window_close'}

