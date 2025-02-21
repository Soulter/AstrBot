'''
Author: diudiu62
Date: 2025-02-18 14:56:30
LastEditTime: 2025-02-18 16:36:24
'''
import aiohttp
import asyncio

async def post_json(base_url, route, token, data):
    headers = {
        'Content-Type': 'application/json'
    }
    if token:
        headers['X-GEWE-TOKEN'] = token

    url = base_url + route

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data, headers=headers, timeout=60) as response:
                response.raise_for_status()
                result = await response.json()

                if result.get('ret') == 200:
                    return result
                else:
                    raise RuntimeError(response.text)
        except Exception as e:
            print(f"http请求失败, url={url}, exception={e}")
            raise RuntimeError(str(e))
