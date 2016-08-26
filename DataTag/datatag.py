# -*- coding: UTF-8 -*-
__author__ = 'waveli'

import os
import os.path
from xml.dom import minidom
import xlrd
import jieba
import time
import sys
import re

reload(sys)
sys.setdefaultencoding('utf-8')

import platform
osclear = 'clear'
oscode = 'utf-8'
if platform.system() == 'Windows':
    class UnicodeStreamFilter:
        def __init__(self, target):
            self.target = target
            self.encoding = 'utf-8'
            self.errors = 'replace'
            self.encode_to = self.target.encoding
        def write(self, s):
            if type(s) == str:
                s = s.decode("utf-8")
            s = s.encode(self.encode_to, self.errors).decode(self.encode_to)
            self.target.write(s)
    if sys.stdout.encoding == 'cp936':
        sys.stdout = UnicodeStreamFilter(sys.stdout)

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

#解析XML文件
def parseXML(filePaths):
    taggedSentences = []
    number = 0
    for filePath in filePaths:
        doc = minidom.parse(filePath)
        # get root element: <employees/>
        root = doc.documentElement
        # get all children elements: <employee/> <employee/>
        entitiesRelations = root.getElementsByTagName("entitiesRelation")
        for entitiesRelation in entitiesRelations:
            number += 1
            taggedsentence = str(entitiesRelation.getElementsByTagName("sentence")[0].childNodes[0].nodeValue)
            if not taggedSentences.__contains__(taggedsentence):
                taggedSentences.append(taggedsentence)
    return [number, taggedSentences]

# 遍历文档目录
def listFileNames(documentPath):
    documentList = []
    for parent,dirnames,filenames in os.walk(documentPath):    #三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        for dirname in  dirnames:                       #输出文件夹信息
            print "parent is:" + parent
            print "dirname is" + dirname

        for filename in filenames:                        #输出文件信息
            # print "parent is:" + parent
            # print "filename is:" + filename
            # print "the full name of the file is:" + os.path.join(parent,filename) #输出文件路径信息
            documentList.append(os.path.join(parent, filename))
    return documentList

#检查句子中的实体数目
def checkSentenceEntity(sentence, dictionary):
    wordlist = []
    for i in range(1, len(dictionary)):
        if sentence.encode('utf-8').__contains__(dictionary[i].encode('utf-8')):
            wordlist.append(dictionary[i].encode('utf-8'))
        i += 1
    return wordlist

# 生成typeA数据结构
def buildDataTypeA(value,number,sentence):
    lables = [',', ':', '->']
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

    entitiesRelation = {'type': "A", 'id': str(number)
    , 'entityBef': str(entityBef), 'entityBefType': str(entityBefType)
    , 'entityAft': str(entityAft), 'entityAftType': str(entityAftType)
    , 'relation': str(relation), 'relationType': str(relationType)
    , 'sentence': str(sentence), 'pubdate': str(pubdate)
    };
    return entitiesRelation

# 生成typeB数据结构
def buildDataTypeB(value,number,sentence):
    lables = [',', '>', '->']
    entitiysTemp = value.split(lables[2])[0]

    entitiyBefTemp = entitiysTemp.split(lables[1])[0]
    entityBef = entitiyBefTemp.split(lables[0])[0]
    entityBefType = entitiyBefTemp.split(lables[0])[1]

    actionBefTemp = entitiysTemp.split(lables[1])[1]
    actionBef = actionBefTemp.split(lables[0])[0]
    actionBefType = actionBefTemp.split(lables[0])[1]



    entitiysTemp = value.split(lables[2])[1]
    entitiyAftTemp = entitiysTemp.split(lables[1])[0]
    entityAft = entitiyAftTemp.split(lables[0])[0]
    entityAftType = entitiyAftTemp.split(lables[0])[1]
    actionAftTemp = entitiysTemp.split(lables[1])[1]
    actionAft = actionAftTemp.split(lables[0])[0]
    actionAftType = actionAftTemp.split(lables[0])[1]

    pubdate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    entitiesRelation = {'type': "B", 'id': str(number)
    , 'entityBef': str(entityBef), 'entityBefType': str(entityBefType)
    , 'entityAft': str(entityAft), 'entityAftType': str(entityAftType)
    , 'actionBef': str(actionBef), 'actionBefType': str(actionBefType)
    , 'actionAft': str(actionAft), 'actionAftType': str(actionAftType)
    , 'sentence': str(sentence), 'pubdate': str(pubdate)
    };
    return entitiesRelation

# 生成xml文件 - typeA: A,Atype:B,Btype->Relation,RelationType
def addEntityRealationTypeA(newEntityRealation,doc,entitiesRelationList):
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

#生成xml文件 - typeB: A,Atype>Action,ActionType->B,Btype>Action,ActionType
def addEntityRealationTypeB(newEntityRealation,doc,entitiesRelationList):
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

    actionBef = doc.createElement("actionBef")
    actionBef.setAttribute("actionBefType", newEntityRealation["actionBefType"])
    actionBef.appendChild(doc.createTextNode(newEntityRealation["actionBef"]))
    entitiesRealion.appendChild(actionBef)

    actionAft = doc.createElement("actionAft")
    actionAft.setAttribute("actionAftType", newEntityRealation["actionAftType"])
    actionAft.appendChild(doc.createTextNode(newEntityRealation["actionAft"]))
    entitiesRealion.appendChild(actionAft)

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

#生成XML文件
def addEntitiesRelations(contents,filePath,documentContents,documentName):
    doc = minidom.Document()
    doc.appendChild(doc.createComment("This is a simple xml."))
    entitiesRelationList = doc.createElement("entitiesRelationList")
    doc.appendChild(entitiesRelationList)

    for content in contents:
        if content['type'] == "A":
            addEntityRealationTypeA(content, doc, entitiesRelationList)
        if content['type'] == "B":
            addEntityRealationTypeB(content, doc, entitiesRelationList)
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

    f = file(filePath, "w")
    doc.writexml(f, encoding='utf-8')
    # doc.writexml(f)
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
    percent = (float(len(taggedFiles) + 1) / float(len(files)))*100
    return str(len(taggedFiles) + 1) + "/" + str(len(files)) + "->" + str(percent)[0:5] + "%"

def showInfo():
    print "***********************EntitiesRelationTagger***********************"
    print "*TagTypeA:  A,Atype:B,Btype->Relation,RelationType                 *"
    print "*TagTypeB:  A,Atype>Action,ActionType->B,Btype>Action,ActionType   *"
    print "********************************************************************"

def showFileInputInfo():
    print "***********************DefaultFileInformation***********************"
    print "*外部词典:           D:\\JinTong\\dict.xlsx                        *"
    print "*待标记文件目录:     D:\\JinTong\\finance                          *"
    print "*标记结果存储目录:   D:\\JinTong\\financeXML                       *"
    print "********************************************************************"

# 检查标记输入格式是否合法
def testTagInput(tagInput):
    # A,Atype:B,Btype->Relation,RelationType
    # A,Atype>Action,ActionType->B,Btype>Action,ActionType
    if re.match(r'(.*),(.*?):(.*?),(.*?)->(.*?),.*', tagInput, re.U):
        return "A"
    elif re.match(r'(.*),(.*?)>(.*?),(.*?)->(.*?),(.*?)>(.*?),.*', tagInput, re.U):
        return "B"
    elif re.match(r'[q|Q]', tagInput, re.U):
        return "Q"
    return ""


if __name__ == '__main__':

    dictionaryPath = "D:\\JinTong\\dict.xlsx"
    documentPath = "D:\\JinTong\\finance"
    documentXMLPath = "D:\\JinTong\\finance" + "XML"
    showFileInputInfo()
    chooseInput = raw_input("是否更改文件路径信息(Y or N):\n")
    if chooseInput == "y" or chooseInput == "Y":
        dictionaryPath = raw_input("请输入领域词库：")
        documentPath = raw_input("请输入待标记的文档目录：")
        documentXMLPath = documentPath + "XML"
    if not os.path.exists(documentXMLPath):
        os.makedirs(documentXMLPath)

    dictionary = getDictionaryContent(dictionaryPath)   #词典内容
    dictionary = list(set(dictionary))                  #词典去重
    #补充分词词典
    for word in dictionary:
        jieba.add_word(word)

    # 标注状态恢复
    state = parseXML(listFileNames(documentXMLPath))
    taggedSentences = state[1]
    relationNumber = state[0]

    # 文档目录文件内容获取
    document = []
    documentPaths = listFileNames(documentPath)
    for documentPath in documentPaths:
        if testTagFile(documentPath):
            documentFo = open(documentPath, "r")
            fileName = documentFo.name
            fileNameWrite = fileName.replace(".txt", ".xml").replace("finance", "financeXML")
            entitiesRelationList = []
            number = 1              # for this document
            documentContent = ''
            while 1:
                line = documentFo.readline()
                documentContent += line
                if not line:
                    break
                if len(line) > 1:
                    for sentence in line.split(lable):
                        wordlist = checkSentenceEntity(sentence, dictionary)
                        if len(wordlist) > 2 and (not taggedSentences.__contains__(sentence)):
                            i = os.system('cls')
                            showInfo()
                            print ''.join(jieba.cut(sentence.strip()))
                            strWord = ''
                            for word in wordlist:
                                strWord += "*" + word.encode('utf-8')
                            print "--------------------------------------------------------------------\n"\
                              + "Possible Entities： " + strWord + "\n" \
                              + "实体关系数：" + str(relationNumber) + ",标记句子总数：" + str(len(taggedSentences)) + ",文件比：" + checkTagFile(documentPaths) + "\n" \
                              + "文件读入路径："+ fileName + "\n" \
                              + "文件写入路径：" + fileNameWrite + "\n"  \
                              + "--------------------------------------------------------------------"
                            taggedSentences.append(sentence)
                            while 1:
                                value = ''
                                tagInputType = ''
                                while 1:
                                    value = raw_input("请正确地标记出本句实体关系(q:next sentence)：\n")
                                    # value = value.decode("GB2312").encode("utf-8")
                                    tagInputType = testTagInput(value)
                                    if len(tagInputType) > 0:
                                        break
                                if tagInputType == "Q":
                                    break
                                entitiesRelation = {}
                                if tagInputType == "A":
                                    entitiesRelation = buildDataTypeA(value, number, sentence)
                                if tagInputType == "B":
                                    entitiesRelation = buildDataTypeB(value, number, sentence)
                                number += 1
                                entitiesRelationList.append(entitiesRelation)
                                relationNumber += 1
            if len(entitiesRelationList) > 0:
                addEntitiesRelations(entitiesRelationList, fileNameWrite, str(documentContent), str(fileName))
            documentFo.close()
            writeTagFile(documentPath)

    print "Thanks for your successful tagged task!!!"