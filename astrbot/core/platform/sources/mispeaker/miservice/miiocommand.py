
import json
from .miioservice import MiIOService


def twins_split(string, sep, default=None):
    pos = string.find(sep)
    return (string, default) if pos == -1 else (string[0:pos], string[pos+1:])


def string_to_value(string):
    if string[0] in '"\'#':
        return string[1:-1] if string[-1] in '"\'#' else string[1:]
    elif string == 'null':
        return None
    elif string == 'false':
        return False
    elif string == 'true':
        return True
    elif string.isdigit():
        return int(string)
    try:
        return float(string)
    except:
        return string

def miio_command_help(did=None, prefix='?'):
    quote = '' if prefix == '?' else "'"
    return f'\
Get Props: {prefix}<siid[-piid]>[,...]\n\
           {prefix}1,1-2,1-3,1-4,2-1,2-2,3\n\
Set Props: {prefix}<siid[-piid]=[#]value>[,...]\n\
           {prefix}2=60,2-1=#60,2-2=false,2-3="null",3=test\n\
Do Action: {prefix}<siid[-piid]> <arg1|[]> [...] \n\
           {prefix}2 []\n\
           {prefix}5 Hello\n\
           {prefix}5-4 Hello 1\n\n\
Call MIoT: {prefix}<cmd=prop/get|/prop/set|action> <params>\n\
           {prefix}action {quote}{{"did":"{did or "267090026"}","siid":5,"aiid":1,"in":["Hello"]}}{quote}\n\n\
Call MiIO: {prefix}/<uri> <data>\n\
           {prefix}/home/device_list {quote}{{"getVirtualModel":false,"getHuamiDevices":1}}{quote}\n\n\
Devs List: {prefix}list [name=full|name_keyword] [getVirtualModel=false|true] [getHuamiDevices=0|1]\n\
           {prefix}list Light true 0\n\n\
MIoT Spec: {prefix}spec [model_keyword|type_urn] [format=text|python|json]\n\
           {prefix}spec\n\
           {prefix}spec speaker\n\
           {prefix}spec xiaomi.wifispeaker.lx04\n\
           {prefix}spec urn:miot-spec-v2:device:speaker:0000A015:xiaomi-lx04:1\n\n\
MIoT Decode: {prefix}decode <ssecurity> <nonce> <data> [gzip]\n\
'


async def miio_command(service: MiIOService, did, text, prefix='?'):
    cmd, arg = twins_split(text, ' ')

    if cmd.startswith('/'):
        return await service.miio_request(cmd, arg)

    if cmd.startswith('prop') or cmd == 'action':
        return await service.miot_request(cmd, json.loads(arg) if arg else None)

    argv = arg.split(' ') if arg else []
    argc = len(argv)
    if cmd == 'list':
        return await service.device_list(argc > 0 and argv[0], argc > 1 and string_to_value(argv[1]), argc > 2 and argv[2])

    if cmd == 'spec':
        return await service.miot_spec(argc > 0 and argv[0], argc > 1 and argv[1])

    if cmd == 'decode':
        return MiIOService.miot_decode(argv[0], argv[1], argv[2], argc > 3 and argv[3] == 'gzip')

    if not did or not cmd or cmd == '?' or cmd == '？' or cmd == 'help' or cmd == '-h' or cmd == '--help':
        return miio_command_help(did, prefix)

    if not did.isdigit():
        devices = await service.device_list(did)
        if not devices:
            return "Device not found: " + did
        did = devices[0]['did']

    props = []
    setp = True
    miot = True
    for item in cmd.split(','):
        key, value = twins_split(item, '=')
        siid, iid = twins_split(key, '-', '1')
        if siid.isdigit() and iid.isdigit():
            prop = [int(siid), int(iid)]
        else:
            prop = [key]
            miot = False
        if value is None:
            setp = False
        elif setp:
            prop.append(string_to_value(value))
        props.append(prop)

    if miot and argc > 0:
        args = [] if arg == '[]' else [string_to_value(a) for a in argv]
        return await service.miot_action(did, props[0], args)

    do_props = ((service.home_get_props, service.miot_get_props), (service.home_set_props, service.miot_set_props))[setp][miot]
    return await do_props(did, props if miot or setp else [p[0] for p in props])
