# -*- coding: utf-8 -*-
# Copyright 2019 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        """
        La función search tiene que ser llamada con API antigua para que funcione la APP.
        En el módulo l10n_es_partner es llamada con API nueva, por tanto tenemos que parchearla
		heredándola y llamámdola con API antigua.
		Nota: poner el módulo donde es llamada con API nueva como dependencia y heredar
        """
        return super(ResPartner, self).search(
            cr, uid, args, offset=offset, limit=limit, order=order,
            context=context, count=count)

