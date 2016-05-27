# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from openerp import models, api


class ProcurementCompute(models.TransientModel):
    _inherit = 'procurement.orderpoint.compute'

    @api.multi
    def procure_calculation(self):
        """
        Calculate orderpoints with SUPERUSER because of intercompany
        procurements
        """
        self.ensure_one()
        rec = self.with_context(use_sudo=True)
        return super(ProcurementCompute, rec).procure_calculation()
