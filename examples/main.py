from crapsolver_python import Crapsolver, Captcha, Sitekey, User

if __name__ == "__main__":
    our_id = "user:123456"
    solver = Crapsolver(our_id)
    sitekey = "a9b5fb07-92ff-493f-86fe-352a2803b3df"

    user: User = solver.get_user() # get info about ourselves to know if we can create a task
    assert user.balance > 0, "Balance needs to be greater than zero"

    print(f"Balance: ${user.balance_dollars:.3f} ({user.balance} Solves)\nThreads: {user.used_threads}/{user.max_threads}\nTotal Solved: {user.solved_hcaptcha}")

    if user.used_threads < user.max_threads:
        sitekey_info: Sitekey = solver.check_sitekey(sitekey) # get info about the sitekey to know if its enabled

        if sitekey_info.enabled:

            captcha: Captcha = solver.solve(
                "discord.com",
                "a9b5fb07-92ff-493f-86fe-352a2803b3df",
                proxy="http://username:password@host:port",
                text_free_entry=True,
                max_retry=5
            ) # create a task and get the captcha pass token
            if isinstance(captcha, Captcha):
                print(captcha.token[:32], captcha.user_agent, captcha.req[:32], sep=" | ")
            else:
                print("error while solving captcha", captcha)

# python -m pip install crapsolver-python==0.0.9
