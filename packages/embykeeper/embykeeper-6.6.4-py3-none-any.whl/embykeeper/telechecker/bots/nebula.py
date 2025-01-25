import asyncio
from json import JSONDecodeError
from urllib.parse import parse_qs, urlencode, urlparse

import httpx
from pyrogram.raw.functions.messages import RequestWebView
from pyrogram.raw.functions.users import GetFullUser
from faker import Faker

from embykeeper.utils import remove_prefix, get_proxy_str

from ..link import Link
from ._base import BaseBotCheckin


class NebulaCheckin(BaseBotCheckin):
    name = "Nebula"
    bot_username = "Nebula_Account_bot"
    max_retries = 1

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.failed = False
        self.timeout *= 3
        self._retries = 0

    async def fail(self):
        self.failed = True
        self.finished.set()

    async def retry(self):
        self._retries += 1
        if self._retries <= self.max_retries:
            await asyncio.sleep(2)
            await self._checkin()
        else:
            self.log.warning("超过最大重试次数.")
            await self.fail()

    async def start(self):
        try:
            try:
                await asyncio.wait_for(self._checkin(), self.timeout)
            except asyncio.TimeoutError:
                pass
        except OSError as e:
            self.log.info(f'发生错误: "{e}".')
            return False
        if not self.finished.is_set():
            self.log.warning("无法在时限内完成签到.")
            return False
        else:
            return not self.failed

    async def _checkin(self):
        bot = await self.client.get_users(self.bot_username)
        self.log.info(f"开始执行签到: [green]{bot.name}[/] [gray50](@{bot.username})[/].")
        bot_peer = await self.client.resolve_peer(self.bot_username)
        user_full = await self.client.invoke(GetFullUser(id=bot_peer))
        url = user_full.full_user.bot_info.menu_button.url
        url_auth = (
            await self.client.invoke(RequestWebView(peer=bot_peer, bot=bot_peer, platform="ios", url=url))
        ).url
        self.log.debug(f"请求面板: {url_auth}")
        scheme = urlparse(url_auth)
        data = remove_prefix(scheme.fragment, "tgWebAppData=")
        url_base = scheme._replace(path="/api/proxy/userCheckIn", query=f"data={data}", fragment="").geturl()
        scheme = urlparse(url_base)
        query = parse_qs(scheme.query, keep_blank_values=True)
        query = {k: v for k, v in query.items() if not k.startswith("tgWebApp")}
        token = await Link(self.client).captcha("nebula")
        if not token:
            self.log.warning("签到失败: 无法获得验证码.")
            return await self.fail()
        useragent = Faker().safari()
        query["token"] = token
        url_checkin = scheme._replace(query=urlencode(query, True)).geturl()
        proxy = get_proxy_str(self.proxy)
        try:
            async with httpx.AsyncClient(http2=True, proxy=proxy) as client:
                resp = await client.get(url_checkin, headers={"User-Agent": useragent})
                results = resp.json()
                message = results["message"]
                if any(s in message for s in ("未找到用户", "权限错误")):
                    self.log.info("签到失败: 账户错误.")
                    await self.fail()
                if "失败" in message:
                    self.log.info("签到失败.")
                    await self.retry()
                    return
                if "已经" in message:
                    self.log.info("今日已经签到过了.")
                    self.finished.set()
                elif "成功" in message:
                    self.log.info(
                        f"[yellow]签到成功[/]: + {results['data']['get_credit']} 分 -> {results['data']['credit']} 分."
                    )
                    self.finished.set()
                else:
                    self.log.warning(f"接收到异常返回信息: {message}")
                    await self.retry()
        except (httpx.HTTPError, OSError, JSONDecodeError) as e:
            self.log.info(f"签到失败: 无法连接签到页面 ({e.__class__.__name__}).")
            await self.retry()
