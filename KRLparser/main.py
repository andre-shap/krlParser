# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
import ui_MyWindow
import sys
import re


class MyWindow(QtWidgets.QMainWindow, ui_MyWindow.Ui_MainWindow):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.adressLine.setText('myProgram.txt')  # Указывание название файла
        self.codeEditor.setPlainText('''DEF my_program()
        
DECL POS HOME
INI
HOME = {A1 0, A2 0, A3 0, A4 0, A5 0, A6 0}

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
        print('Имя файла: ', fileName)
        print('Текст файла:, ', text)
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
            r'^DEF\s(?P<objectName>\w{1,24})\((?P<objectParams>(.+)?)\)$')  # Шаблон для объявления объекта
        declTemplate = re.compile(
            r'^DECL\s(?P<varType>[INT|REAL|BOOL|CHAR|POS]+)\s(?P<varName>\w{1,24})$')  # Шаблон для объявления переменных
        iniTemplate = re.compile(r'INI')  # Шаблон для начала инициализации переменных
        varTemplate = re.compile(r'^(?P<varIni>\w{1,24})\s\=\s(?P<varValue>.+)')
        ptpCommonTemplate = re.compile(r'^PTP\s(?P<pointName>\w{1,24})$')
        linCommonTemplate = re.compile(r'^LIN\s(?P<pointName>\w{1,24})$')
        circCommonTemplate = re.compile(r'^CIRC\s(?P<auxPoint>\w{1,24}),\s(?P<pointName>\w{1,24})$')
        file = open('coordinates.txt', 'w')
        file.close()
        for i in strokes:
            defStroke = re.match(defTemplate, i)
            declStroke = re.match(declTemplate, i)
            varInit = re.match(varTemplate, i)
            ptpCommonStroke = re.match(ptpCommonTemplate, i)
            linCommonStroke = re.match(linCommonTemplate, i)
            circCommonStroke = re.match(circCommonTemplate, i)
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
                    if varInit:
                        print(i)
                        varId = varInit.group('varIni')
                        varValue = varInit.group('varValue')
                        print(varId)
                        print(varValue)
                        name = self.varCorrelator(varId, varValue, varDictionary)[0]
                        value = self.varCorrelator(varId, varValue, varDictionary)[1]
                        varNameDictionary[name] = value
                if ptpCommonStroke:
                    pointName = ptpCommonStroke.group('pointName')
                    motionType = 'PTP'
                    print('Тип движения:', motionType, ', имя точки:', pointName)
                    coordinate = self.coordinateParser(pointName, motionType, varNameDictionary)[0]
                    motionType = self.coordinateParser(pointName, motionType, varNameDictionary)[1]
                    print('Тип движения:', motionType, ',', 'координаты точки:', coordinate)
                    self.angleParser(coordinate, motionType, pointName)
                if linCommonStroke:
                    pointName = linCommonStroke.group('pointName')
                    motionType = 'LIN'
                    print('Тип движения:', motionType, ', имя точки:', pointName)
                    coordinate = self.coordinateParser(pointName, motionType, varNameDictionary)[0]
                    motionType = self.coordinateParser(pointName, motionType, varNameDictionary)[1]
                    print('Тип движения:', motionType, ',', 'координаты точки:', coordinate)
                    self.angleParser(coordinate, motionType, pointName)
        print('Словарь вне функции:', varNameDictionary)

    def varCorrelator(self, varId, varValue, varDictionary):
        iniDict = dict()
        boolTemplate = re.compile(r'[TRUE|FALSE]')
        intTemplate = re.compile(r'\-\d+')
        realTemplate = re.compile(r'\-\d+\.\d+')
        charTemplate = re.compile(r'[a-z,A-Z]+')
        posTemplate = re.compile(r'\{([X|A1]{1,2}\s\-?\d+\.?(\d+)?)?,?\s?([Y|A2]{1,2}\s\-?\d+\.?(\d+)?)?,?\s?([Z|A3]{1,2}\s\-?\d+\.?(\d+)?)?,?\s?([A|A4]{1,2}\s\-?\d+\.?(\d+)?)?,?\s?([B|A5]{1,2}\s\-?\d+\.?(\d+)?)?,?\s?([C|A6]{1,2}\s\-?\d+\.?(\d+)?)?\}')
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
            r'^\{(X\s(?P<x>\-?\d{1,3}\.?(\d{1,2})?),?\s?)?(Y\s(?P<y>\-?\d{1,3}\.?(\d{1,2})?),?\s?)?(Z\s(?P<z>\-?\d{1,3}\.?(\d{1,2})?),?\s?)?(A\s(?P<a>\-?\d{1,3}\.?(\d{1,2})?),?\s?)?(B\s(?P<b>\-?\d{1,3}\.?(\d{1,2})?),?\s?)?(C\s(?P<c>\-?\d{1,3}\.?(\d{1,2})?),?\s?)?\}$')
        angleTemplate = re.compile(
            r'^\{(A1\s(?P<a1>\-?\d{1,3}\.?(\d{1,2})?),?\s?)?(A2\s(?P<a2>\-?\d{1,3}\.?(\d{1,2})?),?\s?)?(A3\s(?P<a3>\-?\d{1,3}\.?(\d{1,2})?),?\s?)?(A4\s(?P<a4>\-?\d{1,3}\.?(\d{1,2})?),?\s?)?(A5\s(?P<a5>\-?\d{1,3}\.?(\d{1,2})?),?\s?)?(A6\s(?P<a6>\-?\d{1,3}\.?(\d{1,2})?),?\s?)?\}$')
        xyzDescription = re.match(xyzTemplate, coordinate)
        angleDescription = re.match(angleTemplate, coordinate)
        file = open('coordinates.txt', 'a')
        file.write(str(motionType) + ' ')
        file.write(str(pointName) + ' ')
        if xyzDescription:
            print('Точка в декартовых координатах')
            file.write('DESC ')
            x = xyzDescription.group('x')
            y = xyzDescription.group('y')
            z = xyzDescription.group('z')
            a = xyzDescription.group('a')
            b = xyzDescription.group('b')
            c = xyzDescription.group('c')
            print('x', x, ',''y', y, ',''z', z, ',''a', a, ',''b', b, ',''c', c)
            # print(type(x))
            coordinatesList = [x, y, z, a, b, c]
            print(coordinatesList)
            print(len(coordinatesList))
            counter = 0
            for i in coordinatesList:

                if counter == len(coordinatesList) - 1:
                    if i is None:
                        print('Нет последнего значения')
                        file.write('Nan ')
                    else:
                        print('Есть последнее значение')
                        file.write(str(i) + ' ')
                    file.write('\n')
                    file.close()
                    break
                else:
                    if i is None:
                        print('Нет значения')
                        file.write('Nan ')
                    else:
                        print('Есть значение')
                        file.write(str(i) + ' ')
                counter += 1
        elif angleDescription:
            print('Точка в обобщенных координатах')
            file.write('ANGL ')
            a1 = angleDescription.group('a1')
            a2 = angleDescription.group('a2')
            a3 = angleDescription.group('a3')
            a4 = angleDescription.group('a4')
            a5 = angleDescription.group('a5')
            a6 = angleDescription.group('a6')
            print('a1', a1, ',''a2', a2, ',''a3', a3, ',''a4', a4, ',''a5', a5, ',''a6', a6)
            coordinatesList = [a1, a2, a3, a4, a5, a6]
            print(coordinatesList)
            print(len(coordinatesList))
            counter = 0
            for i in coordinatesList:
                if counter == len(coordinatesList) - 1:
                    if i is None:
                        print('Нет последнего значения')
                        file.write('Nan ')
                    else:
                        print('Есть последнее значение')
                        file.write(str(i) + ' ')
                    file.write('\n')
                    file.close()
                    break
                else:
                    if i is None:
                        print('Нет значения')
                        file.write('Nan ')
                    else:
                        print('Есть значение')
                        file.write(str(i) + ' ')
                counter += 1


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Windows')
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
