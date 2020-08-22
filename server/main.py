from flask import Flask, render_template, request
from datetime import datetime
import os.path
import pandas as pd

temp_logs = [

]

# id - ip - detector - value
dev = pd.DataFrame(data=[], columns=['id', 'ip', 'detector', 'value'])
logFile = 'logs.csv'
if not os.path.exists(logFile):
    open(logFile, 'tw', encoding='utf-8')


def wLog(*logData):
    logWriter = open(logFile, 'a')
    _data = ''
    for text in logData:
        if not logData[-1] == text:
            _data += str(text) + ';'
        else:
            _data += str(text) + '\n'
    logWriter.write(str(datetime.now().strftime('%Y/%m/%d %H:%M:%S')) + ';' + _data)
    logWriter.close()


app = Flask(__name__)


@app.route('/get_data', methods=['GET'])
def status():
    d = dev.to_json()
    return d


@app.route("/logs", methods=['GET'])
def logs():
    return render_template('logs.html', logs=temp_logs)


@app.route('/send', methods=['POST'])
def send():
    global dev
    device_id = int(request.json['dev_id'])
    _detector = str(request.json['detector'])
    msg = str(request.json['event'])
    if not isinstance(msg, str) or len(msg) == 0 or not isinstance(device_id, int):
        return {"status": False}
    if len(temp_logs) > 40:
        del temp_logs[0]
    ip = request.headers.get('Host')
    print(request.headers)
    wLog(ip, device_id, _detector, msg)
    temp_logs.append({'timestamp': datetime.now().strftime('%Y/%m/%d %H:%M:%S'), 'ip': ip, 'device_id': device_id,
                      'detector': _detector, 'msg': msg})
    k1 = -1
    if dev.shape[0] > 0:
        lst = (dev['id'] == device_id) & (dev['detector'] == _detector)
        k = 0
        for i in lst:
            k += 1
            if i:
                k1 = k
                break
    if k1 > 0:
        dev.loc[(dev['id'] == device_id) & (dev['detector'] == _detector), 'value'] = msg
    else:
        tempData = pd.DataFrame([[device_id, ip, _detector, msg]], columns=['id', 'ip', 'detector', 'value'])
        dev = dev.append(tempData, ignore_index=True)
        # print(tempData + '\n')
        print(dev)
    return {"status": True}


wLog(' --->! Server started!')
app.run(host=str(input('Enter server IP address: ')), port=str(input('Enter port: ')))
