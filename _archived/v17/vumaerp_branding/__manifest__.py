# -*- coding: utf-8 -*-
{
    'name': 'VumaERP Branding',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Replace Odoo branding with VumaERP in client-visible areas',
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'data/mail_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'vumaerp_branding/static/src/js/branding.js',
            'vumaerp_branding/static/src/css/branding.css',
        ],
        'web.assets_frontend': [
            'vumaerp_branding/static/src/css/branding.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
