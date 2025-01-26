from x_client.http import Client as HttpClient

from xync_client.Abc.AuthTrait import BaseAuthTrait
from xync_client.TgWallet.pyro import PyroClient


class AuthClient(BaseAuthTrait):
    async def _get_auth_hdrs(self) -> dict[str, str]:
        pyro = PyroClient(self.agent)
        init_data = await pyro.get_init_data()
        tokens = HttpClient("walletbot.me")._post("/api/v1/users/auth/", init_data)
        self.agent.exid = tokens["user_id"]
        await self.agent.save()
        pref = "" if self.__class__.__name__ == "AssetClient" else "Bearer "
        return {"Wallet-Authorization": tokens["jwt"], "Authorization": pref + tokens["value"]}
