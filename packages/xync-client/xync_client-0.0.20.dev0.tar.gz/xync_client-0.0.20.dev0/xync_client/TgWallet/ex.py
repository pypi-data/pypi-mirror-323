from asyncio import run
from x_model import init_db

from xync_schema import models
from xync_schema.models import Ex, Agent

from xync_client.loader import PG_DSN
from xync_client.Abc.Ex import BaseExClient
from xync_client.Abc.Base import FlatDict, DictOfDicts, MapOfIdsList, ListOfDicts
from xync_client.TgWallet.auth import AuthClient


class ExClient(BaseExClient, AuthClient):
    def __init__(self, ex: Ex):  # ex should be with fetched .agents
        self.agent: Agent = [ag for ag in ex.agents if ag.auth][0]  # need for AuthTrait
        super().__init__(ex)  # , "host_p2p"

    # 19: Список поддерживаемых валют тейкера
    async def curs(self) -> FlatDict:
        coins_curs = await self._post("/p2p/public-api/v2/currency/all-supported")
        return {c["code"]: c["code"] for c in coins_curs["data"]["fiat"]}

    async def _pms(self, cur: str) -> dict[str, dict]:
        pms = await self._post("/p2p/public-api/v3/payment-details/get-methods/by-currency-code", {"currencyCode": cur})
        return {pm["code"]: {"name": pm["nameEng"]} for pm in pms["data"]}

    # 20: Список платежных методов
    async def pms(self, _cur: str = None) -> DictOfDicts:
        pms = {}
        for cur in await self.curs():
            for k, pm in (await self._pms(cur)).items():
                pms.update({k: pm})
        return pms

    # 21: Список платежных методов по каждой валюте
    async def cur_pms_map(self) -> MapOfIdsList:
        return {cur: list(await self._pms(cur)) for cur in await self.curs()}

    # 22: Список торгуемых монет (с ограничениям по валютам, если есть)
    async def coins(self) -> FlatDict:
        coins_curs = await self._post("/p2p/public-api/v2/currency/all-supported")
        return {c["code"]: c["code"] for c in coins_curs["data"]["crypto"]}

    # 23: Список пар валюта/монет
    async def pairs(self) -> MapOfIdsList:
        coins = await self.coins()
        curs = await self.curs()
        pairs = {cur: set(coins.values()) for cur in curs.values()}
        return pairs

    async def _get_ad(self, offer_id: int) -> dict:
        get_ad = await self._post("/p2p/public-api/v2/offer/get", {"offerId": offer_id})
        return get_ad["data"]

    # 24: Список объяв по (buy/sell, cur, coin, pm)
    async def ads(
        self, coin_exid: str, cur_exid: str, is_sell: bool, pm_exids: list[str | int] = None, amount: int = None
    ) -> ListOfDicts:
        params = {
            "baseCurrencyCode": coin_exid,
            "quoteCurrencyCode": cur_exid,
            "offerType": "SALE" if is_sell else "PURCHASE",
            "offset": 0,
            "limit": 100,
            # "merchantVerified": "TRUSTED"
        }
        ads = await self._post("/p2p/public-api/v2/offer/depth-of-market/", params, "data")
        return ads


async def main():
    await init_db(PG_DSN, models, True)
    tgex = await Ex.get(name="TgWallet").prefetch_related("agents", "agents__ex")
    cl = tgex.client()
    e = await cl.pms()
    print(e)


if __name__ == "__main__":
    run(main())
