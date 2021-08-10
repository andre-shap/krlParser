# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
import ui_MyWindow
import sys, re


class MyWindow(QtWidgets.QMainWindow, ui_MyWindow.Ui_MainWindow):

    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.adressLine.setText('myProgram.txt')
        self.codeEditor.setPlainText('''
DEF my_program( )
INI
        
PTP {A1 0, A2 0, A3 0, A4 0, A5 0}
        
PTP {A1 0, A2 0, A3 0, A4 0, A5 0}
        
END''')
        self.compileBtn.clicked.connect(self.parser)

    def parser(self):
        text=self.codeEditor.toPlainText()
        strokes=text.split('\n')
        print(strokes)

        isProgramStarted=False
        dictionary = dict()

        nameOfProgram=''
        for i in strokes:
            if i:
                words=i.split()
                if i[0:3]=='DEF':
                    for j in range (4, len(i)-3):
                        nameOfProgram=nameOfProgram+i[j]
                if i[0:3]=='INI':
                    isProgramStarted = True
                if i[0:3]=='PTP' and isProgramStarted:
                    point=''
                    pointDescription=''
                    if '{' in i and '}' in i:
                        isTherePointDescription = True
                        #print('Я вижу описание точки')
                    else:
                        isTherePointDescription = False
                        #print('Я не вижу описание точки')
                    for j in range (4,len(i)):
                        if not isTherePointDescription:
                            if i[j]!=' ':
                                point = point + i[j]
                            else:
                                break
                        else:
                            pointDescription=pointDescription+i[j]
                    print(pointDescription)
                    self.coordinateParser(pointDescription)

                    dictionary[point]='PTP'
                if i[0:3]=='LIN' and isProgramStarted:
                    point=''
                    for j in range (4, len(i)):
                        if i[j]!=' ':
                            point = point + i[j]
                        else:
                            break
                    dictionary[point]='LIN'
                if i[0:4]=="CIRC" and isProgramStarted:
                    self.logShower.setPlainText('Error: CIRC motion is not represented right now!')
                    point=''
                    aux_point=''
                    counter=0
                    for j in range (5, len(i)):
                        if counter<2:
                            if counter<1:
                                if i[j]!=' ':
                                    aux_point=aux_point+i[j]
                                else:
                                    aux_point=aux_point.rstrip(',')
                                    counter+=1
                            else:
                                if i[j]!=' ':
                                    point=point+i[j]
                                else:
                                    break

                    dictionary[point]=('CIRC', aux_point)
                if i[0:3]=='END' and isProgramStarted:
                    isProgramStarted=False

        #print(nameOfProgram)
        #print(dictionary)
        #self.coordinatesSaver(dictionary)
        self.logShower.setText('Name of program: '+nameOfProgram)

    #def coordinateParser(self, pointDescript):
        #coordinates = dict()
        #for i in pointDescript:
            #if i=='A':

                #coordinates['A'+pointDescript[i+1]]=pointDescript[i+3:i+6]
        #print(coordinates)

    #def coordinatesSaver(self, dictionary):
         #print(dictionary)
         #keys=list(dictionary.keys())



if __name__=='__main__':
    app=QtWidgets.QApplication(sys.argv)
    app.setStyle('Windows')
    window=MyWindow()
    window.show()
    sys.exit(app.exec_())