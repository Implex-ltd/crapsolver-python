"""
A python wrapper for crapsolver
"""
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
        self.client = Client(headers={"authorization": api})

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

            Dict[str, Any]:  A dict containing status code and json data of response
        """
        assert task_type == TaskType.TYPE_ENTERPRISE, "Only enterprise task allowed"

        if not proxy.startswith("http"):
            proxy = "http://" + proxy

        server = next(__server__)

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
                return resp["data"]["token"], resp["data"]["user_agent"]

        return {
            "error": "max retry reached",
            "list": errors,
        }
