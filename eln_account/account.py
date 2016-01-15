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

from osv import fields, osv, orm

class account_journal(osv.osv):
    
    _inherit = 'account.journal'
    
    _columns = {
        'code': fields.char('Code', size=10, required=True, help="The code will be displayed on reports."),
    }
    
    def create(self, cr, uid, vals, context=None):
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
                    #Buscamos otras cuentas bancarias que tenga la empresa y vemos su diario para asignarle al nuevo que vamos a crear
                    #la misma secuencia que tenga cualquiera de los otros
                    obj_bank = self.pool.get('res.partner.bank')
                    obj_bank_ids = obj_bank.search(cr, uid, [('company_id', '=', vals['company_id'])], context=context)
                    bank_data = obj_bank_ids and obj_bank.browse(cr, uid, obj_bank_ids[0], context=context) or False
                    sequence_id = bank_data and bank_data.journal_id and bank_data.journal_id.sequence_id and bank_data.journal_id.sequence_id.id or False
                    vals.update({'sequence_id': sequence_id})
        return super(account_journal, self).create(cr, uid, vals, context)
    
account_journal()
