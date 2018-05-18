# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields, _
from openerp.addons import decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare, float_round


class ResCompany(models.Model):
    _inherit = "res.company"

    intercompany_user_id = fields.Many2one('res.users', string="Default intercompany user", help="This user will be user for intercompany actions", default=1)
