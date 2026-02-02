# -*- coding: utf-8 -*-
{
    'name': 'VumaERP Branding',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'VumaERP White-label Branding',
    'description': """
VumaERP Branding Module
=======================

Replaces Odoo branding with VumaERP branding throughout the application:

* Login page logo and title
* Backend navbar logo
* Browser tab title
* Favicon
* Footer text
* About dialog
* Email templates

This module should be installed on all customer databases.
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'Other proprietary',
    'depends': [
        'base',
        'web',
        'mail',
    ],
    'data': [
        'views/webclient_templates.xml',
        'views/login_templates.xml',
        'data/ir_config_parameter_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'vumaerp_branding/static/src/scss/branding.scss',
            'vumaerp_branding/static/src/js/branding.js',
            'vumaerp_branding/static/src/xml/branding.xml',
        ],
        'web.assets_frontend': [
            'vumaerp_branding/static/src/scss/branding.scss',
        ],
    },
    'installable': True,
    'auto_install': True,
    'application': False,
}
