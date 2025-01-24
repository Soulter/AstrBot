import os
import time
import base64
import hashlib
import hmac
import json

# REGIONS = ['cn', 'de', 'i2', 'ru', 'sg', 'us']


class MiIOService:

    def __init__(self, account=None, region=None):
        self.account = account
        self.server = 'https://' + ('' if region is None or region == 'cn' else region + '.') + 'api.io.mi.com/app'

    async def miio_request(self, uri, data):
        def prepare_data(token, cookies):
            cookies['PassportDeviceId'] = token['deviceId']
            return MiIOService.sign_data(uri, data, token['xiaomiio'][0])
        headers = {'User-Agent': 'iOS-14.4-6.0.103-iPhone12,3--D7744744F7AF32F0544445285880DD63E47D9BE9-8816080-84A3F44E137B71AE-iPhone', 'x-xiaomi-protocal-flag-cli': 'PROTOCAL-HTTP2'}
        resp = await self.account.mi_request('xiaomiio', self.server + uri, prepare_data, headers)
        if 'result' not in resp:
            raise Exception(f"Error {uri}: {resp}")
        return resp['result']

    async def home_request(self, did, method, params):
        return await self.miio_request('/home/rpc/' + did, {'id': 1, 'method': method, "accessKey": "IOS00026747c5acafc2", 'params': params})

    async def home_get_props(self, did, props):
        return await self.home_request(did, 'get_prop', props)

    async def home_set_props(self, did, props):
        return [await self.home_set_prop(did, i[0], i[1]) for i in props]

    async def home_get_prop(self, did, prop):
        return (await self.home_get_props(did, [prop]))[0]

    async def home_set_prop(self, did, prop, value):
        result = (await self.home_request(did, 'set_' + prop, value if isinstance(value, list) else [value]))[0]
        return 0 if result == 'ok' else result

    async def miot_request(self, cmd, params):
        return await self.miio_request('/miotspec/' + cmd, {'params': params})

    async def miot_get_props(self, did, iids):
        params = [{'did': did, 'siid': i[0], 'piid': i[1]} for i in iids]
        result = await self.miot_request('prop/get', params)
        return [it.get('value') if it.get('code') == 0 else None for it in result]

    async def miot_set_props(self, did, props):
        params = [{'did': did, 'siid': i[0], 'piid': i[1], 'value': i[2]} for i in props]
        result = await self.miot_request('prop/set', params)
        return [it.get('code', -1) for it in result]

    async def miot_get_prop(self, did, iid):
        return (await self.miot_get_props(did, [iid]))[0]

    async def miot_set_prop(self, did, iid, value):
        return (await self.miot_set_props(did, [(iid[0], iid[1], value)]))[0]

    async def miot_action(self, did, iid, args=[]):
        result = await self.miot_request('action', {'did': did, 'siid': iid[0], 'aiid': iid[1], 'in': args})
        return result.get('code', -1)

    async def device_list(self, name=None, getVirtualModel=False, getHuamiDevices=0):
        result = await self.miio_request('/home/device_list', {'getVirtualModel': bool(getVirtualModel), 'getHuamiDevices': int(getHuamiDevices)})
        result = result['list']
        return result if name == 'full' else [{'name': i['name'], 'model': i['model'], 'did': i['did'], 'token': i['token']} for i in result if not name or name in i['name']]

    async def miot_spec(self, type=None, format=None):
        if not type or not type.startswith('urn'):
            def get_spec(all):
                if not type:
                    return all
                ret = {}
                for m, t in all.items():
                    if type == m:
                        return {m: t}
                    elif type in m:
                        ret[m] = t
                return ret
            import tempfile
            path = os.path.join(tempfile.gettempdir(), 'miservice_miot_specs.json')
            try:
                with open(path) as f:
                    result = get_spec(json.load(f))
            except:
                result = None
            if not result:
                async with self.account.session.get('http://miot-spec.org/miot-spec-v2/instances?status=all') as r:
                    all = {i['model']: i['type'] for i in (await r.json())['instances']}
                    with open(path, 'w') as f:
                        json.dump(all, f)
                    result = get_spec(all)
            if len(result) != 1:
                return result
            type = list(result.values())[0]

        url = 'http://miot-spec.org/miot-spec-v2/instance?type=' + type
        async with self.account.session.get(url) as r:
            result = await r.json()

        def parse_desc(node):
            desc = node['description']
            # pos = desc.find('  ')
            # if pos != -1:
            #     return (desc[:pos], '  # ' + desc[pos + 2:])
            name = ''
            for i in range(len(desc)):
                d = desc[i]
                if d in '-—{「[【(（<《':
                    return (name, '  # ' + desc[i:])
                name += '_' if d == ' ' else d
            return (name, '')

        def make_line(siid, iid, desc, comment, readable=False):
            value = f"({siid}, {iid})" if format == 'python' else iid
            return f"    {'' if readable else '_'}{desc} = {value}{comment}\n"

        if format != 'json':
            STR_HEAD, STR_SRV, STR_VALUE = ('from enum import Enum\n\n', '\nclass {}(tuple, Enum):\n', '\nclass {}(int, Enum):\n') if format == 'python' else ('', '{} = {}\n', '{}\n')
            text = '# Generated by https://github.com/Yonsm/MiService\n# ' + url + '\n\n' + STR_HEAD
            svcs = []
            vals = []

            for s in result['services']:
                siid = s['iid']
                svc = s['description'].replace(' ', '_')
                svcs.append(svc)
                text += STR_SRV.format(svc, siid)
                for p in s.get('properties', []):
                    name, comment = parse_desc(p)
                    access = p['access']

                    comment += ''.join(['  # ' + k for k, v in [(p['format'], 'string'), (''.join([a[0] for a in access]), 'r')] if k and k != v])
                    text += make_line(siid, p['iid'], name, comment, 'read' in access)
                    if 'value-range' in p:
                        valuer = p['value-range']
                        length = min(3, len(valuer))
                        values = {['MIN', 'MAX', 'STEP'][i]: valuer[i] for i in range(length) if i != 2 or valuer[i] != 1}
                    elif 'value-list' in p:
                        values = {i['description'].replace(' ', '_') if i['description'] else str(i['value']): i['value'] for i in p['value-list']}
                    else:
                        continue
                    vals.append((svc + '_' + name, values))
                if 'actions' in s:
                    text += '\n'
                    for a in s['actions']:
                        name, comment = parse_desc(a)
                        comment += ''.join([f"  # {io}={a[io]}" for io in ['in', 'out'] if a[io]])
                        text += make_line(siid, a['iid'], name, comment)
                text += '\n'
            for name, values in vals:
                text += STR_VALUE.format(name)
                for k, v in values.items():
                    text += f"    {'_' + k if k.isdigit() else k} = {v}\n"
                text += '\n'
            if format == 'python':
                text += '\nALL_SVCS = (' + ', '.join(svcs) + ')\n'
            result = text
        return result

    @staticmethod
    def miot_decode(ssecurity, nonce, data, gzip=False):
        from Crypto.Cipher import ARC4
        r = ARC4.new(base64.b64decode(MiIOService.sign_nonce(ssecurity, nonce)))
        r.encrypt(bytes(1024))
        decrypted = r.encrypt(base64.b64decode(data))
        if gzip:
            try:
                from io import BytesIO
                from gzip import GzipFile
                compressed = BytesIO()
                compressed.write(decrypted)
                compressed.seek(0)
                decrypted = GzipFile(fileobj=compressed, mode='rb').read()
            except:
                pass
        return json.loads(decrypted.decode())

    @staticmethod
    def sign_nonce(ssecurity, nonce):
        m = hashlib.sha256()
        m.update(base64.b64decode(ssecurity))
        m.update(base64.b64decode(nonce))
        return base64.b64encode(m.digest()).decode()

    @staticmethod
    def sign_data(uri, data, ssecurity):
        if not isinstance(data, str):
            data = json.dumps(data)
        nonce = base64.b64encode(os.urandom(8) + int(time.time() / 60).to_bytes(4, 'big')).decode()
        snonce = MiIOService.sign_nonce(ssecurity, nonce)
        msg = '&'.join([uri, snonce, nonce, 'data=' + data])
        sign = hmac.new(key=base64.b64decode(snonce), msg=msg.encode(), digestmod=hashlib.sha256).digest()
        return {'_nonce': nonce, 'data': data, 'signature': base64.b64encode(sign).decode()}
