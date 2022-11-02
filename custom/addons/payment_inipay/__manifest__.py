# -*- coding: utf-8 -*-
{
    'name': 'INIpay Payment Acquirer',
    'category': 'Accounting/Payment',
    'summary': 'Payment Acquirer: INIpay Implementation',
    'description': """INIpay payment acquirer""",
    'version': '1.0',
    'author': 'Linkup Infotech Inc.',
    'website': 'http://link-up.co.kr',
    'depends': ['payment', 'website_sale'],
    'data': [
        'views/payment_views.xml',
        'views/payment_inipay_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'post_init_hook': 'create_missing_journal_for_acquirers',
}
