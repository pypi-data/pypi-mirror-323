from abc import abstractmethod

from xync_client.Abc.Base import BaseClient
from xync_client.Abc.Ex import ListOfDicts, DictOfDicts

from xync_client.Abc.AuthTrait import BaseAuthTrait
from xync_schema.models import OrderStatus, Coin, Cur, Ad, AdStatus, Fiat, Agent
from xync_schema.pydantic import FiatNew


class BaseAgentClient(BaseClient, BaseAuthTrait):  # todo: inherit form Base or from Ex Client?
    def __init__(self, agent: Agent):
        self.agent: Agent = agent
        super().__init__(agent.ex)  # , "host_p2p"

    @abstractmethod
    async def start_listen(self) -> bool: ...

    # 0: Получшение ордеров в статусе status, по монете coin, в валюте coin, в направлении is_sell: bool
    @abstractmethod
    async def get_orders(
        self, status: OrderStatus = OrderStatus.created, coin: Coin = None, cur: Cur = None, is_sell: bool = None
    ) -> ListOfDicts: ...

    # 3N: [T] - Уведомление об одобрении запроса на сделку
    @abstractmethod
    async def request_accepted_notify(self) -> int: ...  # id

    # 1: [T] Запрос на старт сделки
    @abstractmethod
    async def order_request(self, ad_id: int, amount: float) -> dict: ...

    # async def start_order(self, order: Order) -> OrderOutClient:
    #     return OrderOutClient(self, order)

    # 1N: [M] - Запрос мейкеру на сделку
    @abstractmethod
    async def order_request_ask(self) -> dict: ...  # , ad: Ad, amount: float, pm: Pm, taker: Agent

    # 2N: [M] - Уведомление об отмене запроса на сделку
    @abstractmethod
    async def request_canceled_notify(self) -> int: ...  # id

    # # # Fiat
    # 25: Список реквизитов моих платежных методов
    @abstractmethod
    async def my_fiats(self, cur: Cur = None) -> DictOfDicts: ...  # {fiat.exid: {fiat}}

    # 26: Создание реквизита моего платежного метода
    @abstractmethod
    async def fiat_new(self, fiat: FiatNew) -> Fiat: ...

    # 27: Редактирование реквизита моего платежного метода
    @abstractmethod
    async def fiat_upd(self, fiat_id: int, detail: str, name: str = None) -> Fiat: ...

    # 28: Удаление реквизита моего платежного метода
    @abstractmethod
    async def fiat_del(self, fiat_id: int) -> bool: ...

    # # # Ad
    # 29: Список моих объявлений
    @abstractmethod
    async def my_ads(self, status: AdStatus = None) -> ListOfDicts: ...

    # 30: Создание объявления
    @abstractmethod
    async def ad_new(
        self,
        coin: Coin,
        cur: Cur,
        is_sell: bool,
        fiats: list[Fiat],
        amount: str,
        price: float,
        min_fiat: str,
        is_float: bool = True,
        details: str = None,
        autoreply: str = None,
        status: AdStatus = AdStatus.active,
    ) -> Ad.pyd(): ...

    # 31: Редактирование объявления
    @abstractmethod
    async def ad_upd(
        self,
        offer_id: int,
        amount: int,
        fiats: list[Fiat] = None,
        price: float = None,
        is_float: bool = None,
        min_fiat: int = None,
        details: str = None,
        autoreply: str = None,
        status: AdStatus = None,
    ) -> Ad.pyd(): ...

    # 32: Удаление
    @abstractmethod
    async def ad_del(self, offer_id: int) -> bool: ...

    # 33: Вкл/выкл объявления
    @abstractmethod
    async def ad_switch(self, offer_id: int, active: bool) -> bool: ...

    # 34: Вкл/выкл всех объявлений
    @abstractmethod
    async def ads_switch(self, active: bool) -> bool: ...

    # # # User
    # 35: Получить объект юзера по его ид
    @abstractmethod
    async def get_user(self, user_id) -> dict: ...

    # 36: Отправка сообщения юзеру с приложенным файлом
    @abstractmethod
    async def send_user_msg(self, msg: str, file=None) -> bool: ...

    # 37: (Раз)Блокировать юзера
    @abstractmethod
    async def block_user(self, is_blocked: bool = True) -> bool: ...

    # 38: Поставить отзыв юзеру
    @abstractmethod
    async def rate_user(self, positive: bool) -> bool: ...

    # 39: Балансы моих монет
    @abstractmethod
    async def my_assets(self) -> dict: ...
