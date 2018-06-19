# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields, _
from openerp.addons import decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare, float_round


class StockLocation (models.Model):

    _inherit = 'stock.location'

    ### ESTAS 2 FUNCIONES SIRVEN PARA RECUPERAR E INSTANCIAR EL PRODUCTO CON EL USUARIO INTERCOMPAÑIA ###
    @api.model
    def get_pda_location(self, id=False, action=''):
        id = id or self.id
        location = self.sudo(self.get_pda_ic(id)).browse([id])
        if action:
            message = action % self.env.user.name
            location.message_post(message)
        return location

    @api.multi
    def get_pda_ic(self, id=False):
        if not id:
            self.ensure_one()
            id = self.id
        sql = u"select intercompany_user_id from res_company rc where id = (select company_id from stock_location where id = %s)" % id
        self._cr.execute(sql)
        record = self._cr.fetchall()
