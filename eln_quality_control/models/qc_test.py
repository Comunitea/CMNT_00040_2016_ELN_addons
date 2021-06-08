# -*- coding: utf-8 -*-
# Copyright 2020 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api

class QcTest(models.Model):
    _inherit = 'qc.test'
    _order = 'name'

    only_purchases = fields.Boolean('Only for purchases')


class QcTestQuestion(models.Model):
    _inherit = 'qc.test.question'

    test = fields.Many2one(ondelete='cascade')


class QcTestQuestionValue(models.Model):
    _inherit = 'qc.test.question.value'

    @api.multi
    def unlink_orphan_values(self):
        question_value = self.env['qc.test.question.value']
        not_in_question = self.search([('test_line', '=', False)])
        for value in not_in_question:
            in_inspection = self.env['qc.inspection.line'].search([('possible_ql_values', '=', value.id)], limit=1)
            if not in_inspection:
                question_value |= value
        question_value.sudo().unlink()

    @api.multi
    def unlink(self):
        question_value = self.env['qc.test.question.value']
        for value in self:
            if value.test_line:
                value.test_line = False
            else:
                question_value |= value
        return super(QcTestQuestionValue, question_value).unlink()

