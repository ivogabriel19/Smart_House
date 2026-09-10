socketio = 0

def pass_socketio(sck):
    global socketio
    socketio = sck

def socket_emit(event, data):
    global socketio
    socketio.emit(event, data)
