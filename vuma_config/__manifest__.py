# -*- coding: utf-8 -*-
{
    'name': 'VumaCloud Configuration',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Environment-based configuration management',
    'description': """
VumaCloud Configuration
=======================

Provides environment-based configuration for Odoo deployments.

Features:
---------
* Read configuration from .env files
* Manage SMTP settings via environment variables
* Database configuration helpers
* Multi-tenant SaaS support utilities

Environment Variables:
----------------------
* ODOO_DB_HOST - Database host
* ODOO_DB_PORT - Database port
* ODOO_DB_USER - Database user
* ODOO_DB_PASSWORD - Database password
* ODOO_SMTP_HOST - SMTP server host
* ODOO_SMTP_PORT - SMTP server port
* ODOO_SMTP_USER - SMTP username
* ODOO_SMTP_PASSWORD - SMTP password
* ODOO_SMTP_ENCRYPTION - SMTP encryption (none/starttls/ssl)
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'Other proprietary',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'auto_install': False,
    'application': False,
}
