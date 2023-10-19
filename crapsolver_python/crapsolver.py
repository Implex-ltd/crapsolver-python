"""
A python wrapper for crapsolver.
"""
from functools import wraps
from itertools import cycle
from time import sleep
from typing import Any, Dict, Optional, Tuple, Union
from dataclasses import dataclass

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
    The status codes returned by /api/task endpoint.
    """
    STATUS_SOLVING = 0
    STATUS_SOLVED = 1
    STATUS_ERROR = 2


class TaskType:
    """
    The Hcaptcha task type.
    """
    TYPE_ENTERPRISE = 0
    TYPE_NORMAL = 1  # Disabled

@dataclass
class Sitekey:
    """
    Returned by check_sitekey, returns info about a specific sitekey.
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
    Returned by get_user, returns info about a user.
    """
    balance: int
    id: str
    solved_hcaptcha: int
    max_threads: int
    used_threads: int

@dataclass
class Captcha:
    """
    Returned by solve, contains info about the solved captcha.
    """
    token: str
    user_agent: str
    req: str

def check_response(func):
    """
    Converts the Response object to a dictionary.
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
            headers = {
                "authorization": api,
                "user-agent": "crapsolver-py"
            }
        )
        
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
    ) -> Dict[str, Union[int, dict]]:
        """
        Create a new task for solving a captcha.

        Args:
            `task_type` (TaskType, optional): The type of captcha-solving task.
            `domain` (str, required): The domain where the captcha is presented.
            `sitekey` (str, required): The sitekey associated with the captcha..
            `proxy` (str, required): The proxy to use for making requests.
            `useragent` (str, optional): User agent to solve with. Defaults to latest user agent.
            `invisible` (bool, optional): Whether the captcha is invisible. Defaults to False.
            `rqdata` (str, optional): Additional request data. Defaults to an empty string.
            `text_free_entry` (bool, optional): Whether to allow free text entry. Defaults to False.
            `turbo` (bool, optional): Whether turbo mode is enabled. Defaults to False.
            `turbo_st` (int, optional): The turbo mode submit delay (ms). Defaults to 3000 (3s).
            `hc_accessibility` (string, optional): accessibility cookie to use. Defaults to "".
            `oneclick_only` (bool, optional): Whether to only allow insta-pass. Defaults to False.

        Returns:

            Dict[str, Any]:  A dict containing status code and json data of response.
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
        Get information about a sitekey.

        Args:
            sitekey (str): The sitekey to check.

        Returns:
            Union[Sitekey, None]: Sitekey class containing info about the sitekey.
        """
        response = self.client.get(
            f"{self.server}/api/misc/check/{sitekey}"
        )
        jsn = response.json()
        if jsn.get("success"):
            jsn = jsn["data"]
            return Sitekey(
                min_submit = jsn["MinSubmitTime"],
                max_submit = jsn["MaxSubmitTime"],
                domain = jsn["Domain"],
                text_only = jsn["AlwaysText"],
                click_only = jsn["OneclickOnly"],
                enabled = jsn["Enabled"],
                rate = jsn["Rate"]
            )
        return None #R1710

    def get_user(self, user_id: str) -> Union[User, None]:
        """
        Get info regarding a user.

        Args:
            user_id (str): The user_id (example user:123456).

        Returns:
            Union[User, None]: User object containing the info or None if request fails.
        """
        response = self.client.get(
            f"{self.server}/api/user/{user_id}"
        )
        jsn = response.json()
        if jsn.get("success"):
            jsn = jsn["data"]
            return User(
                balance = jsn["balance"],
                id = jsn["id"],
                solved_hcaptcha = jsn["solved_hcaptcha"],
                max_threads = jsn["thread_max_hcaptcha"],
                used_threads = jsn["thread_used_hcaptcha"]
            )

        return None #R1710

    def solve(
        self,
        domain: str,
        sitekey: str,
        proxy: str,
        max_retry: Optional[int] = 5,
        wait_time: Optional[int] = 3000,
        turbo_st: Optional[int] = 3000,
        hc_accessibility: Optional[str] = "",
        useragent: Optional[str] = DEFAULT_UA,
        rqdata: Optional[str] = "",
        text_free_entry: Optional[bool] = False,
        oneclick_only: Optional[bool] = False,
        invisible: Optional[bool] = False,
        turbo: Optional[bool] = False,
        task_type: Optional[TaskType] = TaskType.TYPE_ENTERPRISE,
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
            )
            response = data["resp"]["json"]
            node = data["node"]

            if not response.get("success") or response[0].get("success"):
                continue

            if turbo:
                sleep(turbo_st / 1000)
            else:
                sleep(7)

            resp = self.get_task(node, response["data"][0]["id"])["json"]
            if not resp.get("success") or not resp["data"].get("success"):
                errors.append(resp)
                continue

            while resp["data"]["status"] == STATUS.STATUS_SOLVING:
                resp = self.get_task(node, response["data"][0]["id"])["json"]
                sleep(wait_time / 1000)

            if resp["data"]["status"] == STATUS.STATUS_ERROR:
                errors.append(resp["data"]["error"])
                continue

            if resp["data"]["status"] == STATUS.STATUS_SOLVED:
                return Captcha(
                    token = resp["data"]["token"],
                    user_agent = resp["data"]["user_agent"],
                    req = resp["data"]["req"]
                )

        return {
            "error": "max retry reached",
            "list": errors,
        }
