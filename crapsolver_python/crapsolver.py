"""
A python wrapper for crapsolver\n
"""
from dataclasses import dataclass
from functools import wraps
from itertools import cycle
from time import sleep
from typing import Any, Dict, Optional, Tuple, Union

from httpx import Client, Response

__server__ = cycle(
    [
        "https://node01.nikolahellatrigger.solutions",
        "https://node02.nikolahellatrigger.solutions",
        "https://node03.nikolahellatrigger.solutions",
    ]
)

DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"


class STATUS:
    """
    The status codes returned by /api/task endpoint
    """

    STATUS_SOLVING = 0
    STATUS_SOLVED = 1
    STATUS_ERROR = 2


class TaskType:
    """
    The Hcaptcha task type
    """

    TYPE_ENTERPRISE = 0
    TYPE_NORMAL = 1  # Disabled


@dataclass
class Sitekey:
    """
    Returned by check_sitekey, returns info about a specific sitekey
    """

    min_submit: int
    max_submit: int
    domain: str
    text_only: bool
    click_only: bool
    enabled: bool
    rate: int


@dataclass
class User:
    """
    Returned by get_user, returns info about a user
    """

    balance: int
    balance_dollars: int
    user_id: str
    solved_hcaptcha: int
    max_threads: int
    used_threads: int
    bypass_restricted_sites: bool


@dataclass
class Captcha:
    """
    Returned by solve, contains info about the solved captcha
    """

    token: str
    user_agent: str
    req: str


def check_response(func):
    """
    Converts the Response object to a dictionary
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        node = None
        data: Response = func(*args, **kwargs)

        if isinstance(data, tuple):
            data, node = data

        response_dict = {
            "status": data.status_code,
            "json": data.json(),
        }
        if node:
            return {"resp": response_dict, "node": node}
        return response_dict

    return wrapper


class Crapsolver:
    def __init__(self, api: str) -> None:
        self.client = Client(
            headers={"authorization": api, "user-agent": "crapsolver-py"}
        )
        self.user_id = api

    @property
    def server(self) -> str:
        return next(__server__)

    @check_response
    def new_task(
        self,
        domain: str,
        sitekey: str,
        proxy: str,
        task_type: Optional[TaskType] = TaskType.TYPE_ENTERPRISE,
        useragent: Optional[str] = DEFAULT_UA,
        invisible: Optional[bool] = False,
        rqdata: Optional[str] = "",
        text_free_entry: Optional[bool] = False,
        turbo: Optional[bool] = False,
        turbo_st: Optional[int] = 3000,
        hc_accessibility: Optional[str] = "",
        oneclick_only: Optional[bool] = False,
        href: Optional[str] = "",
        exec: Optional[bool] = False,
        dr: Optional[str] = "",
    ) -> Dict[str, Union[int, dict]]:
        """
        Create a new task for solving a captcha\n

        Args:
            `task_type` (TaskType, optional): The type of captcha-solving task.\n
            `domain` (str, required): The domain where the captcha is presented.\n
            `sitekey` (str, required): The sitekey associated with the captcha.\n
            `proxy` (str, required): The proxy to use for making requests.\n
            `useragent` (str, optional): User agent to solve with. Default: latest user agent.\n
            `invisible` (bool, optional): Whether the captcha is invisible. Default: False.\n
            `rqdata` (str, optional): Additional request data. Default: "".\n
            `text_free_entry` (bool, optional): Whether to allow free text entry. Default: False.\n
            `turbo` (bool, optional): Whether turbo mode is enabled. Default: False.\n
            `turbo_st` (int, optional): The turbo mode submit delay (ms). Default: 3000 (3s).\n
            `hc_accessibility` (string, optional): accessibility cookie to use. Default: "".\n
            `oneclick_only` (bool, optional): Whether to only allow insta-pass. Default: False.\n
            `href` (string, optional): href of the page with the captcha, contained in MotionData.\n
            `exec` (bool, optional): Exec you can gather via motionData.\n
            `dr` (string, optional): URL you can gather via motionData.\n

        Returns:

            `Dict[str, Any]`:  A dict containing status code and json data of response
        """
        assert task_type == TaskType.TYPE_ENTERPRISE, "Only enterprise task allowed"

        if not proxy.startswith("http"):
            proxy = "http://" + proxy

        server = self.server
        return (
            self.client.post(
                f"{server}/api/task/new",
                json={
                    "domain": domain,
                    "site_key": sitekey,
                    "user_agent": useragent,
                    "proxy": proxy,
                    "TaskType": task_type,
                    "invisible": invisible,
                    "rqdata": rqdata,
                    "a11y_tfe": text_free_entry,
                    "turbo": turbo,
                    "turbo_st": turbo_st,
                    "hc_accessibility": hc_accessibility,
                    "oneclick_only": oneclick_only,
                    "href": href,
                    "exec": exec,
                    "dr": dr,
                },
            ),
            server,
        )

    @check_response
    def get_task(self, server: str, task_id: str) -> Dict[str, Union[int, dict]]:
        return self.client.get(
            f"{server}/api/task/{task_id}",
        )

    def check_sitekey(self, sitekey: str) -> Union[Sitekey, None]:
        """
        Get information about a sitekey\n

        Args:
            sitekey (str): The sitekey to check\n

        Returns:
            Union[Sitekey, None]: Sitekey class containing info about the sitekey
        """
        response = self.client.get(f"{self.server}/api/misc/check/{sitekey}")
        jsn = response.json()
        if jsn.get("success"):
            jsn = jsn["data"]
            return Sitekey(
                min_submit=jsn["MinSubmitTime"],
                max_submit=jsn["MaxSubmitTime"],
                domain=jsn["Domain"],
                text_only=jsn["AlwaysText"],
                click_only=jsn["OneclickOnly"],
                enabled=jsn["Enabled"],
                rate=jsn["Rate"],
            )
        return None  # R1710

    def get_user(self, user_id: Optional[str] = None) -> Union[User, None]:
        """
        Get info regarding a user\n

        Args:
            user_id (str): The user_id (example user:123456). Default: our user_id\n

        Returns:
            Union[User, None]: User object containing the info or None if request fails
        """
        if not user_id:
            user_id = self.user_id

        response = self.client.get(f"{self.server}/api/user/{user_id}")
        jsn = response.json()

        if jsn.get("success") and jsn.get("data"):
            jsn = jsn["data"]
            balance = jsn["balance"]
            balance_in_dollars = balance / 2000

            return User(
                balance=balance,
                balance_dollars=balance_in_dollars,
                user_id=jsn["id"],
                solved_hcaptcha=jsn["solved_hcaptcha"],
                max_threads=jsn["thread_max_hcaptcha"],
                used_threads=jsn["thread_used_hcaptcha"],
                bypass_restricted_sites=jsn["settings"]["bypass_restricted_sites"],
            )

        return None  # R1710

    def solve(
        self,
        domain: str,
        sitekey: str,
        proxy: str,
        max_retry: Optional[int] = 100,
        wait_time: Optional[int] = 3000,
        turbo_st: Optional[int] = 3500,
        hc_accessibility: Optional[str] = "",
        useragent: Optional[str] = DEFAULT_UA,
        rqdata: Optional[str] = "",
        text_free_entry: Optional[bool] = False,
        oneclick_only: Optional[bool] = False,
        invisible: Optional[bool] = False,
        turbo: Optional[bool] = False,
        task_type: Optional[TaskType] = TaskType.TYPE_ENTERPRISE,
        href: Optional[str] = "",
        exec: Optional[bool] = False,
        dr: Optional[str] = "",
    ) -> Union[Dict[str, Any], Tuple[str, str]]:
        if turbo:
            if turbo_st > 30000:
                turbo_st = 30000

            elif turbo_st < 1000:
                turbo_st = 1000

        errors = []
        for _ in range(max_retry):
            data: Dict[str, Union[str, dict]] = self.new_task(
                domain=domain,
                sitekey=sitekey,
                task_type=task_type,
                useragent=useragent,
                proxy=proxy,
                invisible=invisible,
                rqdata=rqdata,
                text_free_entry=text_free_entry,
                turbo=turbo,
                turbo_st=turbo_st,
                hc_accessibility=hc_accessibility,
                oneclick_only=oneclick_only,
                href=href,
                exec=exec,
                dr=dr,
            )
            response = data["resp"]["json"]
            node = data["node"]

            if turbo:
                sleep(turbo_st / 1000)
            else:
                sleep(7)

            resp = self.get_task(node, response["data"][0]["id"])["json"]

            while resp["data"]["status"] == STATUS.STATUS_SOLVING:
                resp = self.get_task(node, response["data"][0]["id"])["json"]
                sleep(wait_time / 1000)

            if resp["data"]["status"] == STATUS.STATUS_ERROR:
                errors.append(resp["data"]["error"])
                continue

            if resp["data"]["status"] == STATUS.STATUS_SOLVED:
                return Captcha(
                    token=resp["data"]["token"],
                    user_agent=resp["data"]["user_agent"],
                    req=resp["data"]["req"],
                )

        return {
            "error": "max retry reached",
            "list": errors,
        }
