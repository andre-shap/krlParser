# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
import ui_MyWindow
import sys
import re
import math
import numpy as np

'''

TODO:
1) Разобраться с углами Эйлера
2) Реализовать условия
3) Реализовать циклы
4) Реализовать возможность изменения переменных
5) Протестить

'''


class MyWindow(QtWidgets.QMainWindow, ui_MyWindow.Ui_MainWindow):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.adressLine.setText('myProgram.txt')  # Указывание название файла
        self.codeEditor.setPlainText('''DEF my_program()
        
DECL POS HOME
INI
HOME = {A1 0, A2 0, A3 90, A4 0, A5 0}

PTP HOME
        
PTP HOME
        
END''')  # Назначаем стартовый текст
        self.compileBtn.clicked.connect(self.parser)  # Если нажали "compile", то начинаем парсить
        self.saveBtn.clicked.connect(
            self.codeSaver)  # Если нажали "save", то сохраняем код в файл с указанным в адресной строке именем

    # Функция-слот сохранения кода
    def codeSaver(self):
        fileName = self.adressLine.text()  # считываем имя файла с адресной строки
        text = self.codeEditor.toPlainText()  # считываем код с текстового входа
        #print('Имя файла: ', fileName)
        #print('Текст файла:, ', text)
        adressTemplate = re.compile(r'^\w+\.txt')  # шаблон адресной строки
        adressStroke = re.match(adressTemplate, fileName)  # совпадение шаблону адресной строки
        if adressStroke:  # если совпало
            code = open(fileName, 'w') #сохраняем файл
            code.write(text)
            code.close()
            logStroke = 'File ' + fileName + ' is saved'
            self.logShower.setText(logStroke) # выводим сообщения о сохранении файла
            self.repaint()
        else:  # если не совпало
            logStroke = 'File type error: check file type'
            self.logShower.setText(logStroke) # выводим сообщение о не совпадении имени или типа фйла
            self.logShower.repaint()

    def parser(self):
        isObjectCreated = False  # флаг создания объекта
        isVarIniStarted = False  # флаг начала инициализации переменных
        varDictionary = dict()
        varNameDictionary = dict()
        text = self.codeEditor.toPlainText()
        strokes = text.split('\n')  # Получаем текст в виде списка строк
        defTemplate = re.compile(
            r'^(\s+)?DEF(\s+){1}(?P<objectName>\w{1,24})(\s+)?\((\s+)?(?P<objectParams>(.+)?)\)(\s+)?$')  # Шаблон для объявления объекта
        declTemplate = re.compile(
            r'^(\s+)?DECL(\s+){1}(?P<varType>(INT|REAL|BOOL|CHAR|POS))(\s+){1}(?P<varName>\w{1,24})(\s+)?$')  # Шаблон для объявления переменных
        iniTemplate = re.compile(r'(\s+)?INI(\s+)?')  # Шаблон для начала инициализации переменных
        varTemplate = re.compile(r'^(\s+)?(?P<varIni>\w{1,24})(\s+)?\=(\s+)?(?P<varValue>.+)(\s+)?$')
        ptpCommonTemplate = re.compile(r'^(\s+)?PTP(\s+){1}(?P<pointName>\w{1,24})(\s+)?$')
        linCommonTemplate = re.compile(r'^(\s+)?LIN(\s+){1}(?P<pointName>\w{1,24})(\s+)?$')
        circCommonTemplate = re.compile(r'^(\s+)?CIRC(\s+){1}(?P<auxPoint>\w{1,24}),(\s+){1}(?P<pointName>\w{1,24})$(\s+)?')
        ifTemplate=re.compile(r'^(\s+)?IF(\s+){1}(?P<exeCondition>.+)(\s+){1}THEN(\s+)?$')
        endIfTemplate=re.compile(r'^(\s+)?ENDIF(\s+)?$')

        file = open('coordinates.txt', 'w')
        file.close()
        for i in strokes:
            defStroke = re.match(defTemplate, i)
            declStroke = re.match(declTemplate, i)
            varInit = re.match(varTemplate, i)
            ptpCommonStroke = re.match(ptpCommonTemplate, i)
            linCommonStroke = re.match(linCommonTemplate, i)
            circCommonStroke = re.match(circCommonTemplate, i)
            ifStroke=re.match(ifTemplate, i)
            endIfStroke=re.match(endIfTemplate, i)
            # print(defStroke)
            # print(declStroke)
            # print(varIni)

            if defStroke:
                objectName = defStroke.group('objectName')
                objectParams = defStroke.group('objectParams')
                isObjectCreated = True
            # else:
            # print('Объект не создан')

            if isObjectCreated:
                # print('Объект создан')
                if declStroke:
                    # print('Вижу декларирование переменных')
                    varType = declStroke.group('varType')
                    varName = declStroke.group('varName')
                    varDictionary[varName] = varType
                # else:
                # print('Переменные не были задекларированы')

                if iniTemplate:
                    # print('Вижу начало инициализации переменных')
                    isVarIniStarted = True
                # else:
                # print('Переменные не были инициализированны')
                if isVarIniStarted:
                    isIfStarted=False
                    if varInit:
                        #print(i)
                        varId = varInit.group('varIni')
                        varValue = varInit.group('varValue')
                        #print(varId)
                        #print(varValue)
                        name = self.varCorrelator(varId, varValue, varDictionary)[0]
                        value = self.varCorrelator(varId, varValue, varDictionary)[1]
                        varNameDictionary[name] = value
                if ptpCommonStroke:
                    self.ptpStroke(ptpCommonStroke,varNameDictionary)

                if linCommonStroke:
                    self.linStroke(linCommonStroke,varNameDictionary)
                if ifStroke:
                    isIfStarted=True
                    exeCondition=ifStroke.group('exeCondition')
                    self.ifConditionDeterminer(exeCondition)
                if endIfStroke:
                    isIfStarted=False

        print('Словарь вне функции:', varNameDictionary)

    def ifConditionDeterminer(self, exeCondition):
        #print ('Условие: ', exeCondition)
        conditionTemplate=re.compile(r'^(\s+)?(?P<firstVal>.+)(\s)+(==|<=|>=|<|>)(\s+)?.+(\s+)$')
        conditionMatch=re.match(conditionTemplate, exeCondition)

    def directKinematicsTransformer(self,a1, a2, a3, a4, a5):
        # Параметры Денавита-Хартенберга
        # Если считаем относительно стрелы
        alpha=(-math.pi/2, 0, -math.pi/2, math.pi/2, math.pi/2)
        a=(0, -221.12, 0, 0, 185.52)
        d=(230.6, 0, 0, -224, 0)
        theta=(float(a1)*math.pi/180, float(a2)*math.pi/180+math.pi/2, float(a3)*math.pi/180-math.pi/2, float(a4)*math.pi/180, float(a5)*math.pi/180-math.pi/2)
        # Если считаем относительно сгиба на 90 в третьем джоинте
        '''
        a=(0, -221.12, 0, 0, 185.52)
        alpha=(-math.pi/2, 0, math.pi/2, -math.pi/2, math.pi/2)
        d=(230.6, 0, 0, 224, 0)
        theta=(float(a1)*math.pi/180, float(a2)*math.pi/180+math.pi/2, float(a3)*math.pi/180, float(a4)*math.pi/180, float(a5)*math.pi/180-math.pi/2) 
        '''
        rxList=[]
        ryList=[]
        rzList=[]
        diList = []
        axList = []
        ayList = []
        for i in range (0,5):
            rx=np.array([[1, 0, 0, 0], [0, math.cos(alpha[i]), -math.sin(alpha[i]), 0], [0, math.sin(alpha[i]), math.cos(alpha[i]), 0], [0, 0, 0, 1]])
            rxList.append(rx)
        for i in range (0,5):
            ry=np.array([[math.cos(alpha[i]), 0, math.sin(alpha[i]), 0], [0, 1, 0, 0], [-math.sin(alpha[i]), 0, math.cos(alpha[i]), 0], [0, 0, 0, 1]])
            ryList.append(ry)
        for i in range (0,5):
            rz=np.array([[math.cos(theta[i]), -(math.sin(theta[i])), 0, 0], [math.sin(theta[i]), math.cos(theta[i]), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
            rzList.append(rz)
        for i in range (0,5):
            di=np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, d[i]], [0, 0, 0, 1]])
            diList.append(di)
        for i in range (0,5):
            ax=np.array([[1, 0, 0, a[i]], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
            axList.append(ax)
        for i in range (0,5):
            ay=np.array([[1, 0, 0, 0], [0, 1, 0, a[i]], [0, 0, 1, 0], [0, 0, 0, 1]])
            ayList.append(ay)
        #print('Список матриц rxaplha: ',rxalphaList)
        #print('Список матриц rzthetta: ', rzthettaList)
        #print('Список матриц di: ', diList)
        #print('Список матриц ai: ', aiList)
        hList=[]

        for i in range (0,5):
            #if i!=2 and i != 3:
                rzdi=np.matmul(rzList[i], diList[i])
                #print('Первая матрица:', rzdi)
                rzdiai=np.matmul(rzdi, axList[i])
                #print('Вторая матрица:',rzdiai)
                h=np.matmul(rzdiai, rxList[i])
                #print('Итоговая матрица:',h)
                hList.append(h)
            #else:
                #if i == 2:
                #    rzdi = np.matmul(rzList[i], diList[i])
                #    rzdiai = np.matmul(rzdi, axList[i])
                #    h = np.matmul(rzdiai, ryList[i])
                #    hList.append(h)
               # if i == 3:
                  #  rzdi=np.matmul(rzList[i], diList[i])
                 #   rzdiai=np.matmul(rzdi, ayList[i])
                  #  h = np.matmul(rzdiai, rxList[i])
                    #hList.append(h)
        print('Список итоговых матриц: ', hList)
        unitMatrix=np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        hTotal=np.matmul(unitMatrix, hList[0])
        #print(h)
        for i in range (1,5):
            hTotal=np.matmul(hTotal, hList[i])

        print('Итоговая матрица преобразований:', hTotal)
        p = []
        for i in range (0,3):
            p.append(round(hTotal[i,3], 2))
        print ('Координаты положения актуатора:', p)
        #x=round(hTotal[0,3], 2)
        #y=round(hTotal[1])
        r=hTotal[0:3, 0:3]
        #print(r)
        r11 = round(r[0,0], 2)
        r12 = round(r[0,1], 2)
        r13 = round(r[0,2], 2)
        r21 = round(r[1,0], 2)
        r22 = round(r[1,1], 2)
        r23 = round(r[1,2], 2)
        r31 = round(r[2,0], 2)
        r32 = round(r[2,1], 2)
        r33 = round(r[2,2], 2)
        #print(r11, r12, r13, r21, r22, r23, r31, r32, r33)
        if r31!=1 and r31!=-1:
            bettaAngle=round(math.degrees(-math.atan2(r31, math.sqrt(1-math.pow(r31,2)))), 2)
            gammaAngle=round(math.degrees(math.atan2(r21, r11)), 2)
            alphaAngle=round(math.degrees(math.atan2(r32, r33)), 2)
            print('Углы Эйлера (r31!=+-1):', gammaAngle, bettaAngle, alphaAngle)
        elif r31==1:
            sumGammaAlpha=round(math.degrees(math.atan2(r13, r23)), 2)
            print('Сумма альфы и гаммы (r31=1): ', sumGammaAlpha)
        elif r31==-1:
            difGammaAlpha=round(math.degrees(-math.atan2(r13, r23)), 2)
            print('Разность гаммы и альфы (r31=-1): ', difGammaAlpha)
        #else:
            #if r31!=0:
                #bettaAngle=round(math.degrees(math.cos(r33)), 2)
                #alphaAngle=round(math.degrees(math.sin(0)), 2)
                #gammaAngle=round(math.degrees(math.atan2(r21, r11)), 2)
                #print('Углы Эйлера (r31!=0):', alphaAngle, bettaAngle, gammaAngle)
            #else:
                #bettaAngle=round(math.degrees(math.cos(r33)), 2)
                #alphaAngle=round(math.degrees(math.sin(0)), 2)
                #gammaAngle=round(math.degrees(math.atan2(-r12, -r11)), 2)
                #print('Углы Эйлера (r33=-1):', alphaAngle, bettaAngle, gammaAngle)
    def ptpStroke(self, ptpCommonStroke, varNameDictionary):
        pointName = ptpCommonStroke.group('pointName')
        motionType = 'PTP'
        #print('Тип движения:', motionType, ', имя точки:', pointName)
        coordinate = self.coordinateParser(pointName, motionType, varNameDictionary)[0]
        motionType = self.coordinateParser(pointName, motionType, varNameDictionary)[1]
        #print('Тип движения:', motionType, ',', 'координаты точки:', coordinate)
        self.angleParser(coordinate, motionType, pointName)
        return (pointName, motionType, coordinate)

    def linStroke(self, linCommonStroke, varNameDictionary):
        pointName = linCommonStroke.group('pointName')
        motionType = 'LIN'
        #print('Тип движения:', motionType, ', имя точки:', pointName)
        coordinate = self.coordinateParser(pointName, motionType, varNameDictionary)[0]
        motionType = self.coordinateParser(pointName, motionType, varNameDictionary)[1]
        #print('Тип движения:', motionType, ',', 'координаты точки:', coordinate)
        self.angleParser(coordinate, motionType, pointName)

    def varCorrelator(self, varId, varValue, varDictionary):
        iniDict = dict()
        boolTemplate = re.compile(r'(TRUE|FALSE)')
        intTemplate = re.compile(r'(\-)?\d+')
        realTemplate = re.compile(r'(\-)?\d+\.\d+')
        charTemplate = re.compile(r'[a-z,A-Z]+')
        posTemplate = re.compile(
            r'\{(\s+)?((X|A1)(\s+){1}\-?\d+\.?(\d+)?)?(\s+)?,?(\s+)?((Y|A2)(\s+){1}\-?\d+\.?(\d+)?)?(\s+)?,?(\s+)?((Z|A3)(\s+){1}\-?\d+\.?(\d+)?)?(\s+)?,?(\s+)?((A|A4)(\s+){1}\-?\d+\.?(\d+)?)?(\s+)?,?(\s+)?((B|A5)(\s+){1}\-?\d+\.?(\d+)?)?(\s+)?,?(\s+)?((C|A6)(\s+){1}\-?\d+\.?(\d+)?)?(\s+)?\}')

        boolVar = re.match(boolTemplate, varValue)
        intVar = re.match(intTemplate, varValue)
        realVal = re.match(realTemplate, varValue)
        charVal = re.match(charTemplate, varValue)
        posVal = re.match(posTemplate, varValue)
        for i in varDictionary.keys():
            if i == varId:
                if boolVar or intVar or realVal or charVal or posVal:
                    iniDict[varId] = varValue
                    name = varId
                    value = varValue
        return (name, value)

    def coordinateParser(self, pointName, motionType, varNameDictionary):
        for i in varNameDictionary.keys():
            if i == pointName:
                coordinate = varNameDictionary[i]
        return (coordinate, motionType)

    def angleParser(self, coordinate, motionType, pointName):
        xyzTemplate = re.compile(
            r'^\{(\s+)?(X(\s+){1}(?P<x>\-?\d{1,3}\.?(\d{1,2})?)(\s+)?,?(\s+)?)?(Y(\s+){1}(?P<y>\-?\d{1,3}\.?(\d{1,2})?)(\s+)?,?(\s+)?)?(Z(\s+){1}(?P<z>\-?\d{1,3}\.?(\d{1,2})?)(\s+)?,?(\s+)?)?(A(\s+){1}(?P<a>\-?\d{1,3}\.?(\d{1,2})?)(\s+)?,?(\s+)?)?(B(\s+){1}(?P<b>\-?\d{1,3}\.?(\d{1,2})?)(\s+)?,?(\s+)?)?(C(\s+){1}(?P<c>\-?\d{1,3}\.?(\d{1,2})?)(\s+)?,?(\s+)?)?(\s+)?\}$')
        angleTemplate = re.compile(
            r'^\{(\s+)?(A1(\s+){1}(?P<a1>\-?\d{1,3}\.?(\d{1,2})?)(\s+)?,?(\s+)?)?(A2(\s+){1}(?P<a2>\-?\d{1,3}\.?(\d{1,2})?)(\s+)?,?(\s+)?)?(A3(\s+){1}(?P<a3>\-?\d{1,3}\.?(\d{1,2})?)(\s+)?,?(\s+)?)?(A4(\s+){1}(?P<a4>\-?\d{1,3}\.?(\d{1,2})?)(\s+)?,?(\s+)?)?(A5(\s+){1}(?P<a5>\-?\d{1,3}\.?(\d{1,2})?)(\s+)?,?(\s+)?)?(A6(\s+){1}(?P<a6>\-?\d{1,3}\.?(\d{1,2})?)(\s+)?,?(\s+)?)?(\s+)?\}$')
        xyzDescription = re.match(xyzTemplate, coordinate)
        angleDescription = re.match(angleTemplate, coordinate)
        file = open('coordinates.txt', 'a')
        file.write(str(motionType) + ' ')
        file.write(str(pointName) + ' ')
        if xyzDescription:
            #print('Точка в декартовых координатах')
            file.write('DESC ')
            x = xyzDescription.group('x')
            y = xyzDescription.group('y')
            z = xyzDescription.group('z')
            a = xyzDescription.group('a')
            b = xyzDescription.group('b')
            c = xyzDescription.group('c')
            #print('x', x, ',''y', y, ',''z', z, ',''a', a, ',''b', b, ',''c', c)
            # print(type(x))
            coordinatesList = [x, y, z, a, b, c]
            #print(coordinatesList)
            #print(len(coordinatesList))
            counter = 0
            for i in coordinatesList:

                if counter == len(coordinatesList) - 1:
                    if i is None:
                        #print('Нет последнего значения')
                        file.write('Nan ')
                    else:
                        #print('Есть последнее значение')
                        file.write(str(i) + ' ')
                    file.write('\n')
                    file.close()
                    break
                else:
                    if i is None:
                        #print('Нет значения')
                        file.write('Nan ')
                    else:
                        #print('Есть значение')
                        file.write(str(i) + ' ')
                counter += 1
        elif angleDescription:
            #print('Точка в обобщенных координатах')
            file.write('ANGL ')
            a1 = angleDescription.group('a1')
            a2 = angleDescription.group('a2')
            a3 = angleDescription.group('a3')
            a4 = angleDescription.group('a4')
            a5 = angleDescription.group('a5')
            a6 = angleDescription.group('a6')
            #print('a1', a1, ',''a2', a2, ',''a3', a3, ',''a4', a4, ',''a5', a5, ',''a6', a6)
            coordinatesList = [a1, a2, a3, a4, a5, a6]
            #print(coordinatesList)
            #print(len(coordinatesList))
            counter = 0
            self.directKinematicsTransformer(a1,a2,a3,a4,a5)
            for i in coordinatesList:
                if counter == len(coordinatesList) - 1:
                    if i is None:
                        #print('Нет последнего значения')
                        file.write('Nan ')
                    else:
                        #print('Есть последнее значение')
                        file.write(str(i) + ' ')
                    file.write('\n')
                    file.close()
                    break
                else:
                    if i is None:
                        #print('Нет значения')
                        file.write('Nan ')
                    else:
                        #print('Есть значение')
                        file.write(str(i) + ' ')
                counter += 1


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Windows')
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
