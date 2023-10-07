import httpx, itertools

__server__ = itertools.cycle(
    [
        "https://node01.nikolahellatrigger.solutions",
        "https://node02.nikolahellatrigger.solutions",
    ]
)


class STATUS:
    STATUS_SOLVING = 0
    STATUS_SOLVED = 1
    STATUS_ERROR = 2


class TASK_TYPE:
    TYPE_ENTERPRISE = 0
    # Disabled
    TYPE_NORMAL = 1


class Api:
    def __init__(self, api_key: str = None, user_id: str = None):
        self.client = httpx.Client()
        self.user_id = user_id
        self.api_key = api_key

    def check_response(self, data: httpx.Response):
        return {
            "status": data.status_code,
            "json": data.json(),
        }

    def new_task(
        self,
        task_type: TASK_TYPE = TASK_TYPE.TYPE_NORMAL,
        domain: str = "accounts.hcaptcha.com",
        sitekey: str = "2eaf963b-eeab-4516-9599-9daa18cd5138",
        useragent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        proxy: str = "",
        invisible: bool = False,
        rqdata: str = "",
        text_free_entry: bool = False,
        turbo: bool = False,
        turbo_st: int = 3000,
        hc_accessibility: str = "",
        oneclick_only: bool = False,
    ) -> [dict, str]:
        """
        Create a new task for solving a captcha.

        Args:
            `task_type` (TASK_TYPE, optional): The type of captcha-solving task. Defaults to TASK_TYPE.TYPE_NORMAL.\n
            `domain` (str, optional): The domain where the captcha is presented. Defaults to "accounts.hcaptcha.com".\n
            `sitekey` (str, optional): The sitekey associated with the captcha. Defaults to "2eaf963b-eeab-4516-9599-9daa18cd5138".\n
            `useragent` (str, optional): The user agent to use when making requests. Defaults to a common user agent string.\n
            `proxy` (str, optional): The proxy to use for making requests. Defaults to an empty string.\n
            `invisible` (bool, optional): Whether the captcha is invisible. Defaults to False.\n
            `rqdata` (str, optional): Additional request data. Defaults to an empty string.\n
            `text_free_entry` (bool, optional): Whether free text entry is allowed. Defaults to False.\n
            `turbo` (bool, optional): Whether turbo mode is enabled. Defaults to False.\n
            `turbo_st` (int, optional): The turbo mode submit time in milliseconds. Defaults to 3000 (3s).\n
            `hc_accessibility` (string, optional): hc_accessibility cookie, instant pass normal website.\n
            `oneclick_only` (bool, optional): If captcha images spawn, task will be stopped and error returned.\n

        Returns:\n
            dict: A dictionary containing the task ID.
            str:  task node server address 
        """
        
        server = next(__server__)

        response = self.check_response(
            self.client.post(
                f"{server}/api/task/new",
                json={
                    "domain": domain,
                    "site_key": sitekey,
                    "user_agent": useragent,
                    "proxy": proxy,
                    "task_type": task_type,
                    "invisible": invisible,
                    "rqdata": rqdata,
                    "a11y_tfe": text_free_entry,
                    "turbo": turbo,
                    "turbo_st": turbo_st,
                    "hc_accessibility": hc_accessibility,
                    "oneclick_only": oneclick_only,
                },
            )
        )

        return response, server

    def get_task(self, server: str, task_id: str):
        response = self.check_response(
            self.client.get(
                f"{server}/api/task/{task_id}",
            )
        )

        return response