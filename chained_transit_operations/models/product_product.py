# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, models, fields
import openerp.addons.decimal_precision as dp

from openerp.exceptions import ValidationError

class ProductProduct(models.Model):

    _inherit = 'product.product'

    ### ESTAS 2 FUNCIONES SIRVEN PARA RECUPERAR E INSTANCIAR EL PRODUCTO CON EL USUARIO INTERCOMPAÑIA ###
    @api.model
    def get_pda_product(self, id=False, action=''):
        if not id:
            self.ensure_one()
            id = self.id
        product = self.sudo(self.get_pda_ic(id)).browse([id])
        if action:
            message = action % self.env.user.name
            product.message_post(message)
        return product

    @api.multi
    def get_pda_ic(self, id=False):
        if not id:
            self.ensure_one()
            id = self.id

        sql = u"select intercompany_user_id from res_company rc where id = (select company_id from product_template where id = (select product_tmpl_id from product_product where id = %s))"%id
        self._cr.execute(sql)
        record = self._cr.fetchall()
        return record and record[0][0] or self.env.user.id

