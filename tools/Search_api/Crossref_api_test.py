from Data_crossref_extraction import LiteratureProcessor
from Crossref_api import search_crossref
print("开始测试Crossref API调用及数据处理:")
Test = LiteratureProcessor(search_crossref(query="多元回归分析"))
print(Test.process())

"""
输出结果：
[
  {
    'doi': '10.32629/er.v3i4.2656',
    'title': '数学思想数学活动与小学数学教学',
    'authors': [
      '莉 马'
    ],
    'publication': {
      'journal': '教育研究',
      'volume': '3',
      'issue': '4',
      'pages': None,
      'publisher': 'Frontier Scientific Publishing Pte Ltd',
      'year': 2020
    },
    'url': 'https://doi.org/10.32629/er.v3i4.2656',
    'abstract': '随着现代化社会生活节奏的加快以及信息时代的到来,小学生也面临着更大的学业负担以及升学压力。数学作为小学教育的三大主力课程,却因为学习本身的难度以及理解上的困难,逐渐变成一条巨大的“拦路虎”,许多孩子们谈“虎”色变。让学生更好、更主动、更轻松的接受数学从很久以前就是让无数讲师头痛的“顽疾”。在新课标改革前提下,重视数学思想的运用成为小学数学课堂教学的一抹“亮色”。笔者认为合理运用数学思想,开展数学活动对教学有着事半功倍的好处。',
    'citations': 1,
    'references': 0,
    'language': 'en'
  },
  ……
]
"""