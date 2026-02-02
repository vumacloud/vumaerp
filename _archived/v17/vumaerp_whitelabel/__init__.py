# -*- coding: utf-8 -*-
from . import models


def _post_init_hook(env):
    """Post-installation hook to set up VumaERP branding."""
    # Update system parameters for branding
    IrConfigParam = env['ir.config_parameter'].sudo()

    # Set application title
    IrConfigParam.set_param('web.base.url.title', 'VumaERP')

    # Set database manager title
    IrConfigParam.set_param('database.manager.title', 'VumaERP Database Manager')
