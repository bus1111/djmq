import json
from paho.mqtt import publish

from djmq.models import DeviceType, User, Device
from django.http.response import HttpResponseBadRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models.fields import NOT_PROVIDED

# API Schema
schema = {
    'set_rotation_cycle_length': {'cmd': '11', 'args': [{'length': 3, 'default': 80}]},
    'set_forced_rotation_temp':  {'cmd': '12', 'args': [{'length': 3, 'default': 0}]},
    'set_night_length':          {'cmd': '13', 'args': [{'length': 3, 'default': 480}]},
    'set_max_intake_time':       {'cmd': '14', 'args': [{'length': 2, 'default': 5}]},
    'set_max_exhaust_time':      {'cmd': '15', 'args': [{'length': 2, 'default': 5}]},
    'set_winter_rotation_count': {'cmd': '16', 'args': [{'length': 2, 'default': 5}]},
    'reset':                     {'cmd': '08', 'args': []},
}

@csrf_exempt 
def run_command(request, user_id, device_id):
    # Формат запроса: {"cmd": <cmd name>, "args": [<arg value>...]}
    req = json.loads(request.body.decode('utf-8'))
    cmd = req['cmd']
    cmd_schema = schema.get(cmd)

    # Поиск устройства в БД
    device = get_object_or_404(Device, pk=device_id, owner_id=user_id)

    # Валидация запроса
    if cmd_schema is None:
        return HttpResponseBadRequest("No such command")
    if len(req['args']) != len(cmd_schema['args']):
        return HttpResponseBadRequest("Incorrect number of arguments for this command")

    # Формирование команды для устройства
    mq_cmd = cmd_schema['cmd']
    for arg, schema_arg in zip(req['args'], cmd_schema['args']):
        if len(str(arg)) > schema_arg['length']:
            return HttpResponseBadRequest("Incorrect argument size")
        mq_cmd += f"{arg:0{schema_arg['length']}}"

    # Отправка команды на устройство (брокер локальный)
    publish.single(topic=f"{user_id}/{device_id}/system", payload=mq_cmd)

    # Модификация БД
    if cmd.startswith('set'):
        attr = cmd.lstrip('set_')
        setattr(device, attr, req['args'][0])
    elif cmd == 'reset':
        for field in device._meta.fields:
            if field.default != NOT_PROVIDED:
                setattr(device, field.name, field.default)
    device.save()

    return HttpResponse(f"u={user_id}, d={device_id}, cmd={mq_cmd}")


def update_firmware(request, user_id, device_id):
    device_type = request.headers['Device-Type'][:2]
    ver_type = request.headers['Device-Type'][2:]
    device_version = request.headers['Device-Version']

    current_version = get_object_or_404(DeviceType, type=device_type).latest_version
    device = get_object_or_404(Device, pk=device_id, owner_id=user_id)

    if current_version != device_version:
        path = "VK" + device_type + str(ver_type) + "V" + current_version + ".bin"
        print(path)
        device.version = current_version
        device.save()
        f = open(path, "rb")
        return HttpResponse(f, content_type='application/octet-stream')
    else:
        return HttpResponse(status=304)


def create_user(request, name):
    u = User(name=name)
    u.save()
    return HttpResponse(f"n={name}")

def create_device(request, owner_id):
    d = Device(owner=User(pk=owner_id))
    d.save()
    return HttpResponse(f"o={owner_id}")