# -*- coding: utf-8 -*-
from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _get_translation_frontend_modules_name(cls):
        mods = super()._get_translation_frontend_modules_name()
        return mods + ['vumaerp_whitelabel']

    def session_info(self):
        """Override to inject VumaERP branding into session info."""
        result = super().session_info()
        result['server_version_info'] = [17, 0, 0, 'final', 0, 'VumaERP']
        result['support_url'] = 'https://vumacloud.com/support'
        result['vumaerp_branding'] = {
            'name': 'VumaERP',
            'version': '17.0',
            'tagline': 'Enterprise Resource Planning',
            'support_url': 'https://vumacloud.com/support',
            'documentation_url': 'https://vumacloud.com/docs',
            'website': 'https://vumacloud.com',
        }
        return result
