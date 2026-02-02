# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re


class ResPartner(models.Model):
    _inherit = 'res.partner'

    gh_tin = fields.Char(
        string='Ghana TIN',
        size=11,
        help='Ghana Tax Identification Number'
    )
    gh_tin_validated = fields.Boolean(
        string='TIN Validated',
        default=False,
        copy=False
    )

    @api.constrains('gh_tin')
    def _check_gh_tin(self):
        """Validate Ghana TIN format."""
        tin_pattern = re.compile(r'^[A-Z]\d{10}$|^\d{11}$')
        for partner in self:
            if partner.gh_tin:
                if not tin_pattern.match(partner.gh_tin):
                    raise ValidationError(_(
                        'Invalid Ghana TIN format. TIN must be 11 characters.'
                    ))

    @api.onchange('gh_tin')
    def _onchange_gh_tin(self):
        """Reset validation when TIN changes."""
        if self.gh_tin:
            self.gh_tin = self.gh_tin.upper()
        self.gh_tin_validated = False
