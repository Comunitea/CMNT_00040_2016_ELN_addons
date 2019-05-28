# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 QUIVAL, S.A. All Rights Reserved
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

from openerp import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    code = fields.Char('Code', size=10, required=True, 
        help="The code will be displayed on reports.")
    
    @api.model
    def create(self, vals):
        """Cuando se crea un diario contable, si no trae en vals la secuencia,
        se crea una secuencia nueva. Con este cambio a los diarios tipo 'bank', si no trae secuencia en vals,
        asignamos la secuencia que tenga cualquier otro diario de este tipo para la misma compañía.
        Está pensado para cuando creamos cuentas de bancos para la compañía ya que 
        al crear automaticamente el diario del banco no le asigna secuencia y por tanto se creaba una nueva
        pero realmente debe tener la misma para toda la compañía por requisitos legales en España.
        """
        if not 'sequence_id' in vals or not vals['sequence_id']:
            if 'type' in vals and 'company_id' in vals:
                if vals['type'] == 'bank':
                    # Buscamos otras cuentas bancarias que tenga la empresa y vemos su diario para asignarle al nuevo que vamos a crear
                    # la misma secuencia que tenga cualquiera de los otros
                    bank_id = self.env['res.partner.bank'].search(
                        [('company_id', '=', vals['company_id'])],
                        limit=1)
                    sequence_id = bank_id.journal_id.sequence_id.id
                    vals.update({'sequence_id': sequence_id})
        return super(AccountJournal, self).create(vals)


class AccountMove(models.Model):
    _inherit = "account.move"
    
    @api.multi
    def write(self, vals):
        if vals.get('ref', False):
            self._cr.execute(""" UPDATE account_move_line SET ref=%s WHERE move_id=%s""", (vals['ref'], self.id))
        return super(AccountMove, self).write(vals)

    @api.multi
    def button_cancel(self):
        # Impide cancelar un asiento de un periodo cerrado
        for move in self:
            self.env['account.move.line']._update_journal_check(move.journal_id.id, move.period_id.id)
        return super(AccountMove, self).button_cancel()


