# -*- coding: UTF-8 -*-
__author__ = 'waveli'

import os
import os.path
from xml.dom import minidom
import xlrd
import jieba
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import platform
osclear = 'clear'
oscode = 'utf-8'
if platform.system() == 'Windows':
    import WinLinux
    osclear = 'CLS'
    oscode = 'gbk'

lable = '。'

# # 打开词典文件 for txt
# def getDictionaryContent(dictionaryPath):
#     dictionary = []
#     dictionaryFo = open(dictionaryPath, "r")
#     while 1:
#         lines = dictionaryFo.readlines(100000)
#         if not lines:
#             break
#         for line in lines:
#             dictionary.append(line)
#     dictionaryFo.close()
#     return dictionary

# 打开词典文件 for excel
def getDictionaryContent(dictionaryPath):
    dictionary = []
    data = xlrd.open_workbook(dictionaryPath)
    table = data.sheet_by_index(0) #通过索引顺序获取
    dictionary = table.col_values(2)
    return dictionary

# 遍历文档目录
def listFileNames(documentPath):
    documentList = []
    for parent,dirnames,filenames in os.walk(documentPath):    #三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        for dirname in  dirnames:                       #输出文件夹信息
            print "parent is:" + parent
            print  "dirname is" + dirname

        for filename in filenames:                        #输出文件信息
            # print "parent is:" + parent
            # print "filename is:" + filename
            # print "the full name of the file is:" + os.path.join(parent,filename) #输出文件路径信息
            documentList.append(os.path.join(parent,filename))
    return documentList

#检查句子中的实体数目
def checkSentenceEntity(sentence, dictionary):
    wordlist = []
    for i in range(1, len(dictionary)):
        if sentence.encode('utf-8').__contains__(dictionary[i].encode('utf-8')):
            wordlist.append(dictionary[i].encode('utf-8'))
        i += 1
    return wordlist

#生成xml文件
def addEntityRealation(newEntityRealation,doc,entitiesRelationList):
    entitiesRealion = doc.createElement("entitiesRelation")
    entitiesRealion.setAttribute("id", newEntityRealation["id"])

    entityBef = doc.createElement("entityBef")
    entityBef.setAttribute("entityBefType",newEntityRealation["entityBefType"])
    entityBef.appendChild(doc.createTextNode(newEntityRealation["entityBef"]))
    entitiesRealion.appendChild(entityBef)

    entityAft = doc.createElement("entityAft")
    entityAft.setAttribute("entityAftType",newEntityRealation["entityAftType"])
    entityAft.appendChild(doc.createTextNode(newEntityRealation["entityAft"]))
    entitiesRealion.appendChild(entityAft)

    relation = doc.createElement("relation")
    relation.setAttribute("relationType",newEntityRealation["relationType"])
    relation.appendChild(doc.createTextNode(newEntityRealation["relation"]))
    entitiesRealion.appendChild(relation)

    sentence = doc.createElement("sentence")
    sentence.appendChild(doc.createTextNode(newEntityRealation["sentence"]))
    entitiesRealion.appendChild(sentence)

    # fileName = doc.createElement("fileName")
    # fileName.appendChild(doc.createTextNode(newEntityRealation["fileName"]))
    # entitiesRealion.appendChild(fileName)

    pubdate = doc.createElement("pubdate")
    pubdate.appendChild(doc.createTextNode(newEntityRealation["pubdate"]))
    entitiesRealion.appendChild(pubdate)

    entitiesRelationList.appendChild(entitiesRealion)


def addEntitiesRelations(contents,filePath,documentContents,documentName):
    doc = minidom.Document()
    doc.appendChild(doc.createComment("This is a simple xml."))
    entitiesRelationList = doc.createElement("entitiesRelationList")
    doc.appendChild(entitiesRelationList)

    for content in contents:
        addEntityRealation(content,doc,entitiesRelationList)

    operateDates = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    documentContent = doc.createElement("documentContent")
    documentContent.appendChild(doc.createTextNode(documentContents))
    entitiesRelationList.appendChild(documentContent)

    fileName = doc.createElement("fileName")
    fileName.appendChild(doc.createTextNode(str(documentName)))
    entitiesRelationList.appendChild(fileName)

    operateDate = doc.createElement("operateDate")
    operateDate.appendChild(doc.createTextNode(str(operateDates)))
    entitiesRelationList.appendChild(operateDate)

    f = file(filePath,"w")
    doc.writexml(f)
    f.close()

def writeTagFile(filePath):
    fo = open("TaggedFiles.txt", "a+")
    fo.write(filePath + "\n")
    # 关闭打开的文件
    fo.close()

def testTagFile(filePath):
    # 打开一个文件
    fo = open("TaggedFiles.txt", "a+")
    taggedFiles = []
    while 1:
        line = fo.readline()
        if not line:
            break
        taggedFiles.append(line)
    fo.close()
    for linePath in taggedFiles:
        if linePath == (filePath+"\n"):
            return False
    return True

def checkTagFile(files):
    # 打开一个文件
    fo = open("TaggedFiles.txt", "r")
    taggedFiles = []
    while 1:
        line = fo.readline()
        if not line:
            break
        taggedFiles.append(line)
    # 关闭打开的文件
    fo.close()
    return str(len(taggedFiles) + 1) + "/" + str(len(files))

def showInfo():
    print "***********************EntitiesRelationTag***********************"
    print "*Entities:股票类,A;股票类,A;股票类,A;股票类,A;股票类,A;股票类,A;*"
    print "*Relation:收益比,1;收益比,2;收益比,3;收益比,4;收益比,5;收益比,6;*"
    print "*****************************************************************"
	

if __name__ == '__main__':
    # dictionaryPath = raw_input("请输入领域词库：")
    # documentPath = raw_input("请输入待标记的文档目录：")

    dictionaryPath = "E:\\JinTong\\dict.xlsx"
    documentPath = "E:\\JinTong\\finance"

    dictionary = getDictionaryContent(dictionaryPath)   #词典内容
    dictionary = list(set(dictionary))                  #词典去重
    #补充分词词典
    for word in dictionary:
        jieba.add_word(word)

    #文档目录文件内容获取
    document = []
    sentenceTagNumber = 0
    documentPaths = listFileNames(documentPath)
    for documentPath in documentPaths:
        if testTagFile(documentPath):
            documentFo = open(documentPath, "r")
            fileName = documentFo.name
            entitiesRelationList = []
            number = 0              #for this document
            documentContent = ''
            while 1:
                line = documentFo.readline()
                documentContent += line
                if not line:
                    break
                if len(line) > 1:
                    for sentence in line.split(lable):
                        wordlist = checkSentenceEntity(sentence, dictionary)
                        if len(wordlist) > 2:
                            i = os.system('cls')
                            showInfo()
                            print ''.join(jieba.cut(sentence.strip()))
                            strWord = ''
                            for word in wordlist:
                                strWord += "*" + word.encode('utf-8')
                            print "-----------------------------------------------------------------\n"\
                                  + "Possible Entities: " + strWord + "\n" \
                                  + "标注文件比：" + checkTagFile(documentPaths) + ",文件路径："+ fileName + "\n"  + \
                                  "-----------------------------------------------------------------"
                            sentenceTagNumber += 1  #for all document
                            while 1:
                                value = raw_input("请标记出本句实体关系(A,Atype:B,Btype->Realtion,RealtionType)(q:quit)：\n")
                                # lables = ['，', '：', '->']
                                lables = [',', ':', '->']
                                if value == "q":
                                    break
                                relationTemp = value.split(lables[2])[1]
                                relation = relationTemp.split(lables[0])[0]
                                relationType = relationTemp.split(lables[0])[1]

                                entitiysTemp = value.split(lables[2])[0]
                                entitiyBefTemp = entitiysTemp.split(lables[1])[0]
                                entityBef = entitiyBefTemp.split(lables[0])[0]
                                entityBefType = entitiyBefTemp.split(lables[0])[1]

                                entitiyAftTemp = entitiysTemp.split(lables[1])[1]
                                entityAft = entitiyAftTemp.split(lables[0])[0]
                                entityAftType = entitiyAftTemp.split(lables[0])[1]

                                pubdate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                                number += 1
                                entitiesRelation = {'id': str(number)
                                    , 'entityBef': str(entityBef), 'entityBefType': str(entityBefType)
                                    , 'entityAft': str(entityAft), 'entityAftType': str(entityAftType)
                                    , 'relation': str(relation), 'relationType': str(relationType)
                                    , 'sentence': str(sentence), 'pubdate': str(pubdate)
                                    };
                                entitiesRelationList.append(entitiesRelation)
            if len(entitiesRelationList) > 0:
                addEntitiesRelations(entitiesRelationList, fileName.replace(".txt",".xml").replace("finance","financeXML"), str(documentContent), str(fileName))
            documentFo.close()
            writeTagFile(documentPath)

    print sentenceTagNumber