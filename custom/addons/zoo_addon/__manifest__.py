# -*- coding: utf-8 -*-
{
    'name': "Zoo Addon",  # Module title
    'summary': "Zoo Addon",  # Module subtitle phrase
    'description': """
    """,
    'author': "Shin Jun Ho",
    'website': "http://www.example.com",
    'category': 'Uncategorized',
    'version': '14.0.1',
    'depends': ['sale','zoo_manager','stock', 'base', 'purchase'],
    'data': [
            'views/zoo_sales.xml',
            'views/zoo_purchase.xml',
    ],

    # This demo data files will be loaded if     db initialize with demo data (commented because file is not added in this example)
    # 'demo': [
    #     'demo.xml'
    # ],
}


