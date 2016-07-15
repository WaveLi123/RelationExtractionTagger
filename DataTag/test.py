# -*- coding: UTF-8 -*-
__author__ = 'waveli'

# from datatag import checkSentenceEntity
#
# dictionary = ['word_ch','中国','日本']
# sentence = '中国是个有着悠久历史的国家，则没有'
#
# print checkSentenceEntity(sentence,dictionary)

# import jieba
# jieba.add_word("中国美")
# print('/'.join(jieba.cut("中国美日本差")))

from datatag import addEntitiesRelations

addEntitiesRelations()