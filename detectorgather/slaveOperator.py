import requests
import serial
import time
import sys
import glob

server_ip = str(input('Server IP: '))
server_port = str(input('Server port: '))
passw = b'E209229'
connectedState = False
data = ['', '', '']
cntr = 0


def changeVals(_realport):
    global data, cntr
    while 1:
        val = _realport.read()  # для удобства записываем вход с порта
        if val != b'':
            if val == b';':
                try:
                    response = requests.post('http://' + server_ip + ':' + server_port + '/send',
                                             json={'dev_id': int(data[0]), 'detector': data[1], 'event': data[2]})
                    print(response.status_code)
                    print({'dev_id': int(data[0]), 'detector': data[1], 'event': data[2]})
                finally:
                    data[0] = ''
                    data[1] = ''
                    data[2] = ''
                    pass
                cntr = 0
            else:
                tempvar = str(val).replace('b\'', '')
                tempvar = tempvar.replace('\'', '')
                if tempvar == '=':
                    cntr += 1
                else:
                    if cntr == 1:
                        data[0] += tempvar
                    if cntr == 2:
                        data[1] += tempvar
                    if cntr == 3:
                        data[2] += tempvar


def connect(ports):  # вызов от searchForPort
    global connectedState
    for i in ports:  # для попытки подключения
        try:  # пробуем каждый порт
            print("Trying ", i, "...")  # реализуем экземпляр порта
            realport = serial.Serial(port=i, baudrate=115200, timeout=3)
            time.sleep(2)  # даем 2 секунды на соединение
            if realport:  # если порт готов, то отправляем послание
                realport.write(b'search')  # b - означает байтовый код
            raw_msg = realport.readline()  # считываем ответ из порта
            if raw_msg == b'imArduino':  # если ответ - imArduino - значит мы попали
                print("Arduino found")
                realport.write(passw)  # handshake секретной фразой
                raw_msg = realport.readline()
                # print(raw_msg)
                if raw_msg == b'ok\n':  # Если ардуино сказала ОК - значит
                    connectedState = True  # подключились
                    print("connected at ", i)
                    realport.timeout = 0
                    return realport  # возвращаем хорошие новости
            else:
                print("Not responding")
                realport.close()
        except Exception as e:
            print(e)
            pass
    return False


def searchForPort():  # ищем порт, вызов из функции
    if sys.platform.startswith('win'):  # refreshClicked
        ports = ['COM%s' % (i + 1) for i in range(256)]  # для каждой платформы свой способ
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    result = []
    for port in ports:  # пробуем порты на exception
        try:  # если нет эксепшена - запоминаем
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    if result:  # если порты имеются - продолжаем
        print(result)  # запускаем метод подключения по handshake
        p = connect(result)  # если успех - запуск чтения буфера serial
        if p:
            changeVals(p)


searchForPort()
