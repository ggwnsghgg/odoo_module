# -*- coding: utf-8 -*-
{
    'name': "Zoo Manager",  # Module title
    'summary': "Zoo Manager",  # Module subtitle phrase
    'description': """
Zoo Food Data
==============
동물원 동물 식단 관리 매니저
    """,  # Supports reStructuredText(RST) format
    'author': "Shin Jun Ho",
    'website': "http://www.example.com",
    'category': 'Tools',
    'version': '14.0.1',
    'depends': ['base', 'sale'],

    'data': [
            'security/groups.xml',
            'security/ir.model.access.csv',
            'views/zoo_manger.xml',
            'views/zoo_food_table.xml',
    ],

    # This demo data files will be loaded if db initialize with demo data (commented because file is not added in this example)
    # 'demo': [
    #     'demo.xml'
    # ],
}



