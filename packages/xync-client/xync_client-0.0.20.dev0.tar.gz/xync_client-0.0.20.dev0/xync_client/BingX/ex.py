from asyncio import run

from x_model import init_db
from xync_client.Abc.Base import DictOfDicts, FlatDict
from xync_schema import models
from xync_schema.models import Ex

from xync_client.Abc.Ex import BaseExClient
from xync_client.BingX.base import BaseBingXClient
from xync_client.loader import PG_DSN


class ExClient(BaseExClient, BaseBingXClient):
    headers: dict[str, str] = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        "app_version": "9.0.5",
        "device_id": "ccfb6d50-b63b-11ef-b31f-ef1f76f67c4e",
        "lang": "ru-RU",
        "platformid": "30",
        'device_brand': 'Linux_Chrome_131.0.0.0',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    async def _pms(self, cur):
        pms = await self._get("/api/c2c/v1/advert/payment/list", params={"fiat": cur})
        return pms["data"]

    # 19: Список всех платежных методов на бирже
    async def pms(self) -> DictOfDicts:  # {pm.exid: pm}
        curs = await self.curs()
        pp = {}
        for _id, cur in curs.items():
            pms = await self._pms(cur)
            [pp.update({p["id"]: {"name": p["name"], "logo": p["icon"]}}) for p in pms["paymentMethodList"]]
        return pp

    # 20: Список поддерживаемых валют на BingX
    async def curs(self) -> FlatDict:  # {cur.exid: cur.ticker}
        params = {
            "type": "1",
            "asset": "USDT",
            "coinType": "2",
        }
        curs = await self._get("/api/c2c/v1/common/supportCoins", params=params)
        return {cur["id"]: cur["name"] for cur in curs["data"]["coins"]}
    
    # 21: cur_pms_map на BingX
    async def cur_pms_map(self):

        curs = await self.curs()
        pp = {}
        for cur in curs.values():
            pms = await self._pms(cur)
            pp.update({cur : [p["id"] for p in pms["paymentMethodList"]]})
        return pp

    # 22: Монеты на BingX
    async def coins(self) -> FlatDict:
        return {1: "USDT"}

    # 23: Список пар валюта/монет
    async def pairs(self):
        coins = await self.coins()
        curs = await self.curs()
        return {cur: set(coins) for cur in curs.values()}

    # 24: ads
    async def ads(self, coin_exid: str, cur_exid: str, is_sell: bool, pm_exids: list[str | int] = None):
        params = {
            'type': 1,
            'fiat': cur_exid,
            'asset': coin_exid,
            'amount': '',
            'hidePaymentInfo': '',
            'payMethodId': pm_exids if pm_exids else '',
            'isUserMatchCondition': 'true' if is_sell else 'false'
        }

        ads = await self._get("/api/c2c/v1/advert/list", params=params)
        return ads['data']['dataList']


async def main():
    _ = await init_db(PG_DSN, models, True)
    bg = await Ex.get(name="BingX")
    cl = ExClient(bg)
    await cl.curs()
    # pms = await cl.pms()
    await cl.close()


if __name__ == "__main__":
    run(main())
