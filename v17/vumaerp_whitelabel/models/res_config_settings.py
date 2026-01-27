# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    vumaerp_app_name = fields.Char(
        string='Application Name',
        config_parameter='vumaerp.app_name',
        default='VumaERP',
    )
    vumaerp_support_url = fields.Char(
        string='Support URL',
        config_parameter='vumaerp.support_url',
        default='https://vumacloud.com/support',
    )
    vumaerp_documentation_url = fields.Char(
        string='Documentation URL',
        config_parameter='vumaerp.documentation_url',
        default='https://vumacloud.com/docs',
    )
