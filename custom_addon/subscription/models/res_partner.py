# -*- coding: utf-8 -*-
from odoo import api, fields, models, re, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    establishment_id = fields.Char()
    account_id = fields.Many2one(comodel_name='partner.account.id')
    active = fields.Boolean(default=True)

    _sql_constraints = ([
        ('establishment_uniq',
         'unique(establishment_id)',
         'Choose another value - it has to be unique!')
    ])

    @api.constrains('establishment_id')
    def _check_establishment_id(self):
        """ validate Establishment field"""
        pattern = r'^(?=.*[a-zA-Z]{3})(?=.*[0-9]{3})(?=.*[\W_]{3}).{9,}$'
        if self.establishment_id == 0:
            raise ValidationError("Your establishment_id should contain 3alphabet,3numbers,3special characters: %s"
                                  % self.establishment_id)
        elif not re.match(pattern, self.establishment_id):
            raise ValidationError("Your establishment_id should contain 3alphabet,3numbers,3special characters: %s"
                                  % self.establishment_id)

    @api.onchange('display_name')
    def _onchange_name(self):
        """while creating a partner create an account_id using the name of the partner"""
        if self.display_name:
            self.account_id = self.env['partner.account.id'].create({
                'account_id': self.display_name + '@@@111',
            })

    def unlink(self):
        """while deleting partner the account_id will bw deleted"""
        for record in self:
            record.account_id.unlink()
        return super().unlink()
