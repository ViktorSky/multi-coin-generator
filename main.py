from uuid import uuid4 as uuid_gen
from time import time as timestamp
from base64 import b64encode
from json import loads, dumps
from threading import Thread
from random import randint
from hashlib import sha1
from hmac import new
import asyncio
import os


os.system("pip install -r requirements.txt")

from json_minify import json_minify
from aiofile import async_open
from flask import Flask
from aiohttp import (
    ClientSession
)

import box


Parameters = {
    "community-link":
        "http://aminoapps.com/invite/5G0A09Y6RE",

    "proxy": None
}

###################$
emailsPath = "acc.json"
###################


signatureKey="f8e7a61ac3f725941e3ac7cae2d688be97f30b93"
deviceKey="02b258c63559d8804321c5d5065af320358d366f"


GRAY = lambda *text, type = 1: f"\033[{type};30m" + " ".join(str(obj) for obj in text) + "\033[0m"

RED = lambda *text, type = 1: f"\033[{type};31m" + " ".join(str(obj) for obj in text) + "\033[0m"

GREEN = lambda *text, type = 1: f"\033[{type};32m" + " ".join(str(obj) for obj in text) + "\033[0m"

YELLOW = lambda *text, type = 1: f"\033[{type};33m" + " ".join(str(obj) for obj in text) + "\033[0m"

BLUE = lambda *text, type = 1: f"\033[{type};34m" + " ".join(str(obj) for obj in text) + "\033[0m"

MAGNETA = lambda *text, type = 1: f"\033[{type};35m" + " ".join(str(obj) for obj in text) + "\033[0m"

CYAN = lambda *text, type = 1: f"\033[{type};36m" + " ".join(str(obj) for obj in text) + "\033[0m"


#-----------------FLASK-APP-----------------
app = Flask(__name__)
@app.route('/')
def home():
    return "~~8;> ~~8;>"
#----------------------------------------------------



class Amino:

    def __init__(
        self: object,
        device: str = None,
        proxy: str = None,
        uuid: str = None
    ) -> None:

        self.proxy = proxy
        self.device = device or None
        self.session = ClientSession()
        self.uuid = uuid or str(uuid_gen()) #"b89d9a00-f78e-46a3-bd54-6507d68b343c" 
        self.userId, self.sid = None, None



    def __del__(self):
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self._close_session())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self._close_session())



    async def _close_session(self):
        if not self.session.closed:
            await self.session.close()



    async def device_gen(
        self: object,
        device_info: bytes = bytes.fromhex("42") + os.urandom(20)
    ) -> str:

        new_device: str = (
            device_info + new(
                bytes.fromhex(deviceKey),
                device_info,
                sha1
            ).digest()
        ).hex().upper()
        return new_device



    async def headers(
        self: object,
        data: str = None
    ) -> dict:

        if not self.device:
            self.device = await self.device_gen()

        headers = {
            "NDCDEVICEID": self.device,
            "SMDEVICEID": self.uuid,
            "Accept-Language": "en-EN",
            "Content-Type":
                "application/json; charset=utf-8",
            "User-Agent":
                'Dalvik/2.1.0 (Linux; U; Android 7.1; LG-UK495 Build/MRA58K; com.narvii.amino.master/3.3.33180)', 
            "Host": "service.narvii.com",
            "Accept-Encoding": "gzip",
            "Connection": "keep-alive"
        }

        if data is not None:
            headers["Content-Length"] = str(len(data))
            headers["NDC-MSG-SIG"] = await self.sig(data)

        if self.sid is not None:
            headers["NDCAUTH"] = "sid=%s" % self.sid

        return headers



    async def sig(
        self, data: (str, dict) = None
    ) -> str:

        signature: str = b64encode(
            bytes.fromhex("42") + new(
                bytes.fromhex(signatureKey),
                data.encode("utf-8"),
                sha1
            ).digest()
        ).decode("utf-8")
        return signature



    async def request(
        self: object,
        method: str,
        url: str,
        data: dict = None,
        minify: bool = False,
        **kwargs: dict
    ) -> dict:

        assert method.upper() in ("DELETE", "GET", "POST", "PUT"), "Invalid method -> %r" % method

        url = f"https://service.narvii.com/api/v1/{url}"

        if self.sid is not None:
            url += f"?sid={self.sid}"

        if isinstance(data, dict):
            data["timestamp"] = int(timestamp() * 1000)
            data = dumps(data)

            if minify is True:
                data = json_minify(data)

        async with self.session.request(
            method = method.upper(),
            url = url,
            headers = await self.headers(data = data),
            data = data,
            proxy = self.proxy
        ) as response:

            try: return await response.json()
            except: raise Exception(await response.text())



    async def get_from_code(
        self: object,
        code: str
    ) -> dict:

        return await self.request(
            method = "GET",
            url = f"g/s/link-resolution?q={code}"
        )



    async def login(
        self: object,
        email: str,
        password: str,
        secret: str = None,
    ) -> dict:

        data = {
            "email": email,
            "v": 2,
            "secret": f"0 {password}" if not secret else secret,
            "deviceID": self.device,
            "clientType": 100,
            "action": "normal",
        }

        resp = await self.request(
            method = "POST",
            url = "g/s/auth/login",
            data = data
        )

        self.sid = resp.get("sid", None)
        self.userId = resp.get("account", {}).get("uid", None)

        return resp.copy()



    async def join_community(
        self: object,
        comId: int,
        invitationId: str
    ) -> dict:

        data = {}

        if invitationId:
            data["invitationId"] = invitationId

        resp = await self.request(
            method = "POST",
            url = f"x{comId}/s/community/join",
            data = data
        )

        return resp.copy()



    async def lottery(
        self: object,
        comId: int,
        tz: (int, str)
    ) -> dict:

        data = {
            "timezone": tz,
        }

        resp = await self.request(
            method = "POST",
            url = f"x{comId}/s/check-in/lottery",
            data = data
        )

        return resp.copy()



    async def watch_ad(
        self: object
    ) -> dict:

        resp = await self.request(
            method = "POST",
            url = "g/s/wallet/ads/video/start"
        )

        return resp.copy()



    async def send_active_obj(
        self: object,
        comId: int,
        tz: int,
        timers: list
    ) -> dict:

        data = {
            "userActiveTimeChunkList": timers,
            "optInAdsFlags": 2147483647,
            "timezone": tz
        }

        resp = await self.request(
            method = "POST",
            url = f"x{comId}/s/community/stats/user-active-time",
            data = data,
            minify = True
        )

        return resp.copy()





class Generator(object):

    joined = False
    logged = 0


    async def get_community(
        self,
        amino: object = None
    ) -> None:

        fromcode = await amino.get_from_code(
            code = Parameters.get("community-link")
        )

        extensions = fromcode.get("linkInfoV2", {}).get("extensions", {})

        self.comId = extensions["community"].get("ndcId", None)
        self.invitationId = extensions.get("invitationId", None)



    async def login_task(
        self: object,
        amino: object,
        email: str,
        password: str,
        sleep: int
    ) -> None:

        await asyncio.sleep(1 * sleep)
        resp = await amino.login(
            email = email,
            password = password
        )

        print("[" + BLUE("login") + f"][{email}]: {resp['api:message']}.")



    async def join_community_task(
        self: object,
        amino: object,
        email: str,
        sleep: int
    ) -> None:

        await asyncio.sleep(1 * sleep)
        resp = await amino.join_community(
            comId = self.comId,
            invitationId = self.invitationId
        )
        
        print("[" + CYAN("join-community") + f"][{email}]: {resp['api:message']}.")



    async def lottery_task(
        self: object,
        amino: object,
        email: str,
        sleep: int
    ) -> None:

        await asyncio.sleep(1.5 * sleep)
        resp = await amino.lottery(
            comId = self.comId,
            tz = box.tzFilter(hour = 23)
        )

        print("[" + GREEN("lottery") + f"][{email}]: {resp['api:message']}")



    async def watch_ad_task(
        self: object,
        amino: object,
        email: str,
        sleep: int
    ) -> None:

        await asyncio.sleep(1 * sleep)
        resp = await amino.watch_ad()

        print("[" + YELLOW("watch-ad") + f"][{email}]: {resp['api:message']}.")


    async def send_active_obj_task(
        self: object,
        amino: object,
        email: str,
        sleep: int
    ) -> None:

        await asyncio.sleep(3 * sleep)
        resp = await amino.send_active_obj(
            comId = self.comId,
            tz = box.tzFilter(hour = 23),
            timers = list({
                "start": int(timestamp()),
                "end": int(timestamp() + 300)
            } for _ in range(50)),
        )

        print("[" + MAGNETA("main-proccess") + f"][{email}]: {resp['api:message']}.")



    async def run(
        self: object
    ) -> None:
 
        await self.get_community(Amino(
            proxy = Parameters.get("proxy")
        ))
 
        await asyncio.sleep(1)

        if not os.path.exists(emailsPath):
            print(emailsPath, "file does not exist. Run get_accounts.py to create it.")
            exit(1)

        async with async_open(emailsPath, "r") as File:
            accounts = loads(await File.read())

        apps = [
            Amino(
                device = x["device"],
                uuid = x.get("uuid", None),
                proxy = Parameters.get("proxy")
            ) for x in accounts
        ]

        while True:
            try:
                # login task
                if (timestamp() - self.logged) >= 60 * 60 * 23:
                    print()
                    await asyncio.gather(*(
                        self.login_task(
                            amino = amino,
                            email = x["email"],
                            password = x["password"],
                            sleep = sleep
                        ) for sleep, (amino, x) in enumerate(
                            zip(apps, accounts)
                        )
                    )); print()

                # join community task
                if self.joined is False:
                    await asyncio.gather(*(
                        self.join_community_task(
                            amino = amino,
                            email = x["email"],
                            sleep = sleep
                        ) for sleep, (amino, x) in enumerate(
                            zip(apps, accounts)
                        )
                    )); print()

                    self.joined = True

                # lottery task
                if (timestamp() - self.logged) >= 60 * 60 * 23:
                    await asyncio.gather(*(
                        self.lottery_task(
                            amino = amino,
                            email = x["email"],
                            sleep = sleep
                        ) for sleep, (amino, x) in enumerate(
                            zip(apps, accounts)
                        )
                    )); print()

                    self.logged = int(timestamp())

                # watch ad task
                await asyncio.gather(*(
                    self.watch_ad_task(
                        amino = amino,
                        email = x["email"],
                        sleep = sleep
                    ) for sleep, (amino, x) in enumerate(
                        zip(apps, accounts)
                    )
                )); print()

                # 24 task of send active object
                for _ in range(24):
                    await asyncio.gather(*(
                        self.send_active_obj_task(
                            amino = amino,
                            email = x["email"],
                            sleep = sleep
                        ) for sleep, (amino, x) in enumerate(
                            zip(apps, accounts)
                        )
                    ))

                    await asyncio.sleep(3)
                    print()

            except Exception as Error:
                print(f"[" + RED(["email"]) + "]][" + RED("error") + f"]]: {str([Error]).strip('[]')}")



async def main() -> None:
    if not Parameters.get("community-link", "")[::-1][:Parameters.get("community-link", "")[::-1].index("/")][::-1]:
        print("Community not detected in %r" % 'Parameters["community-link"]')
        exit()

    Thread(
        target = app.run,
        kwargs = {
            "host": "0.0.0.0",
            "port": randint(2000, 9000)
        }
    ).start()

    generator = Generator()
    await generator.run()


if __name__ == "__main__":
    box.clear()
    asyncio.run(main())
