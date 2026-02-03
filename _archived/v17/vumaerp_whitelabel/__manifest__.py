# -*- coding: utf-8 -*-
{
    'name': 'VumaERP White Label',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Complete white-labeling: Replace all Odoo references with VumaERP',
    'description': """
VumaERP White Label Module
==========================

This module completely rebrands the system to VumaERP by replacing all
Odoo references throughout the application including:

* Login page branding
* Web client interface (navbar, menus, about dialog)
* Loading screens and spinners
* Email templates and footers
* Portal and website pages
* Database manager
* System parameters
* Browser tab title and favicon

Configuration:
--------------
After installation, go to Settings > General Settings > VumaERP Branding
to customize company-specific branding options.
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'portal',
    ],
    'data': [
        'data/ir_config_parameter_data.xml',
        'views/webclient_templates.xml',
        'views/login_templates.xml',
        'views/email_templates.xml',
        'views/portal_templates.xml',
        'views/database_manager_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'vumaerp_whitelabel/static/src/css/whitelabel.css',
            'vumaerp_whitelabel/static/src/js/whitelabel.js',
        ],
        'web.assets_frontend': [
            'vumaerp_whitelabel/static/src/css/whitelabel_frontend.css',
        ],
        'web._assets_primary_variables': [
            ('prepend', 'vumaerp_whitelabel/static/src/css/primary_variables.css'),
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'post_init_hook': '_post_init_hook',
}
