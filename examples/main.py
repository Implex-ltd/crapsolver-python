from crapsolver_python import Crapsolver, Captcha, Sitekey, User

if __name__ == "__main__":
    solver = Crapsolver("example")
    our_id = "user:123456"
    sitekey = "b2b02ab5-7dae-4d6f-830e-7b55634c888b"

    user: User = solver.get_user(our_id) # get info about ourselves to know if we can create a task
    assert user.balance > 0, "Balance needs to be greater than zero"

    print(f"Balance: ${user.balance}\nThreads: {user.used_threads}/{user.max_threads}\nTotal Solved: {user.solved_hcaptcha}")

    if user.used_threads < user.max_threads:
        sitekey_info: Sitekey = solver.check_sitekey(sitekey) # get info about the sitekey to know if its enabled

        if sitekey_info.enabled:

            captcha: Captcha = solver.solve(
                domain=sitekey_info.domain,
                sitekey=sitekey,
                proxy="http://username:password@ip:port",
                text_free_entry=True,
                turbo=True,
                turbo_st=3500,
            ) # create a task and get the captcha pass token

            print(captcha.token[:32], captcha.user_agent, captcha.req[:32], sep=" | ")

# python -m pip install crapsolver-python==0.0.5
