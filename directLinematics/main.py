import math
import numpy as np



print("Введите обобщенные координаты манипулятора")
print('Введите a1: ')
a1 = float(input())
print('Введите a2: ')
a2 = float(input())
print('Введите a3: ')
a3 = float(input())
print('Введите a4: ')
a4 = float(input())
print('Введите a5: ')
a5 = float(input())

# a1=0
# a2=0
# a3=0
# a4=0
# a5=0
# Параметры Денавита-Хартенберга
# Если считаем относительно стрелы

"""
alpha=(-math.pi/2, 0, -math.pi/2, math.pi/2, math.pi/2)
a=(0, -221.12, 0, 0, 185.52)
d=(230.6, 0, 0, -224, 0)
theta=(float(a1)*math.pi/180, float(a2)*math.pi/180+math.pi/2, float(a3)*math.pi/180-math.pi/2, float(a4)*math.pi/180, float(a5)*math.pi/180-math.pi/2)
"""

# Если считаем относительно сгиба на 90 в третьем джоинте
a=(0, -221.12, 0, 0, 185.52)
alpha=(-math.pi/2, 0, math.pi/2, -math.pi/2, math.pi/2)
d=(230.6, 0, 0, 224, 0)
theta=(float(a1)*math.pi/180, float(a2)*math.pi/180+math.pi/2, float(a3)*math.pi/180, float(a4)*math.pi/180, float(a5)*math.pi/180-math.pi/2) 

#Списки для хранения матриц, показывающих вклады каждого из параметров
#Вращение относительно осей x (зависят от alpha)
rxList=[]
#Вращение относительно осей z (зависят от theta, что зависят от a1...a5)
rzList=[]
#Перемещение относительно осей z (зависят от d)
diList = []
#Перемещение относительно осей x (зависят от a)
axList = []
ryList = []

# Памятка: 'a1...a5' - обобщенные координаты, 'a' - один из параметров Денавита-Хартенберга
# Заполнение списков матриц, описывающие вклады каждого параметра Денавита-Хартенберга
for i in range (0,5):
    rx=np.array([[1, 0, 0, 0], [0, math.cos(alpha[i]), -math.sin(alpha[i]), 0], [0, math.sin(alpha[i]), math.cos(alpha[i]), 0], [0, 0, 0, 1]])
    rxList.append(rx)
for i in range (0,5):
    rz=np.array([[math.cos(theta[i]), -(math.sin(theta[i])), 0, 0], [math.sin(theta[i]), math.cos(theta[i]), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    rzList.append(rz)
for i in range (0,5):
    di=np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, d[i]], [0, 0, 0, 1]])
    diList.append(di)
for i in range (0,5):
    ax=np.array([[1, 0, 0, a[i]], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    axList.append(ax)

# Список для хранения матриц преобразования (ориентация+положение) каждого звена
hList=[]

for i in range (0,5):
        rzdi=np.matmul(rzList[i], diList[i])
        #print('Первая матрица:', rzdi)
        rzdiai=np.matmul(rzdi, axList[i])
        #print('Вторая матрица:',rzdiai)
        h=np.matmul(rzdiai, rxList[i])
        #print('Итоговая матрица:',h)
        hList.append(h)
#print('Список итоговых матриц: ', hList)
# Единичная матрица
unitMatrix=np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
# Перемножение матриц преобразования каждого звена - получение общей матрицы преобразования
hTotal=np.matmul(unitMatrix, hList[0])
for i in range (1,5):
    hTotal=np.matmul(hTotal, hList[i])
#print('Итоговая матрица преобразований:', hTotal)
# Список для хранения декартовых координат (x,y,z) общей матрицы преобразования
p = []
for i in range (0,3):
    p.append(round(hTotal[i,3], 2))
print ('Координаты положения актуатора:', p)
# Выделение матрицы вращения из общей матрицы преобразования
r=hTotal[0:3, 0:3]
#print(r)
# Все элементы матрицы вращения отдельно
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
# Поиск углов Тейта-Брайана согласно матрице вращения в порядке ZYX


#Информация для получения матрицы вращения в порядке ZYX на углы альфа(alp), бетта(bet), гамма(gam)
'''
alp=0
bet=0
gam=0

#Rzyx=Rz*Ry*Rx
Rz=np.array([[math.cos(alp), -math.sin(alp), 0],
            [math.sin(alp), math.cos(alp), 0],
            [0, 0, 1]])
Ry=np.array([[math.cos(bet), 0, math.sin(bet)],
            [0, 1, 0],
            [-math.sin(bet), 0, math.cos(bet)]])
Rx=np.array([[1, 0, 0],
             [0, math.cos(gam), -math.sin(gam)],
             [0, math.sin(gam), math.cos(gam)]])

Rzyx=np.array([[math.cos(alp)*math.cos(bet), -math.sin(alp)*math.cos(gam)+math.cos(alp)*math.sin(bet)*math.sin(gam), math.sin(alp)*math.sin(gam)+math.cos(alp)*math.sin(bet)*math.cos(gam)],
               [math.sin(alp)*math.cos(bet), math.cos(alp)*math.cos(gam)+math.sin(alp)*math.sin(bet)*math.sin(gam), -math.cos(alp)*math.sin(gam)+math.sin(alp)*math.sin(bet)*math.cos(gam)],
               -math.sin(bet), math.cos(bet)*math.sin(gam), math.cos(bet)*math.cos(gam)])
'''

if r31!=1 and r31!=-1:
    bettaAngle=round(math.degrees(math.asin(-r31)), 2)
    #bettaAngle=round(math.degrees(-math.atan2(r31, math.sqrt(1-math.pow(r31,2)))), 2)
    alphaAngle=round(math.degrees(math.atan2(r21, r11)), 2)
    gammaAngle=round(math.degrees(math.atan2(r32, r33)), 2)
    print('Углы Тейта-Брайана(ZYX) (r31!=+-1): ', alphaAngle, bettaAngle, gammaAngle)
elif r31==-1:
    #В таком случае можно использовать один из 2 способов поиска разности gamma и alpha
    difGammaAlpha=round(math.degrees(math.atan2(r12, r22)), 2)
    bettaAngle = round(math.degrees(math.asin(-r31)), 2)
    #bettaAngle = round(math.degrees(-math.atan2(r31, math.sqrt(1 - math.pow(r31, 2)))), 2)
    print('Разность гамма и альфа (r31==-1): ', difGammaAlpha)
    # Из-за того, что мы на данном этапе можно получить только разность альфа и гамма
    # нужно принять один из этих углов за некую величину (например, 0) и получить вторую

    #print('Можно посчитать только разность гамма и альфа. Введите альфа: ')
    #alphaAngle=float(input())
    alphaAngle=0
    gammaAngle=difGammaAlpha+alphaAngle
    print('Углы Тейта-Брайана(ZYX) (r31==-1) (alphaAngle='+str(alphaAngle)+'): ', alphaAngle, bettaAngle, gammaAngle)
    # print('Можно посчитать только разность гамма и альфа. Введите гамма: ')
    # gammaAngle=float(input())
    gammaAngle = 0
    alphaAngle = difGammaAlpha - gammaAngle
    print('Углы Тейта-Брайана(ZYX) (r31==-1) (gammaAngle='+str(gammaAngle)+'): ', alphaAngle, bettaAngle, gammaAngle)
elif r31==1:
    sumGammaAlpha=round(math.degrees(math.atan2(r12, r13)), 2)
    print('Сумма гамма и альфа (r31==1): ', sumGammaAlpha)
    # Из-за того, что мы на данном этапе можно получить только сумму альфа и гамма
    # нужно принять один из этих углов за некую величину (например, 0) и получить вторую
    bettaAngle = round(math.degrees(math.asin(-r31)), 2)
    #bettaAngle = round(math.degrees(-math.atan2(r31, math.sqrt(1 - math.pow(r31, 2)))), 2)

    # print('Можно посчитать только сумму гамма и альфа. Введите альфа: ')
    # alphaAngle=float(input())
    alphaAngle = 0
    gammaAngle = sumGammaAlpha - alphaAngle
    print('Углы Тейта-Брайана(ZYX) (r31==1): ', alphaAngle, bettaAngle, gammaAngle)

    # print('Можно посчитать только сумму гамма и альфа. Введите гамма: ')
    # gammaAngle=float(input())
    gammaAngle = 0
    alphaAngle = sumGammaAlpha - gammaAngle
    print('Углы Тейта-Брайана(ZYX) (r31==1): ', alphaAngle, bettaAngle, gammaAngle)





