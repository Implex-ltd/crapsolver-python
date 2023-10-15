from crapsolver_python import Crapsolver

if __name__ == "__main__":
    w = Crapsolver()

    token = w.solve(
        domain="discord.com",
        sitekey="b2b02ab5-7dae-4d6f-830e-7b55634c888b",
        proxy="http://brd-customer-hl_eb0b0971-zone-data_center-ip-154.30.99.246:y1v966s05ykg@brd.superproxy.io:22225",
        text_free_entry=True,
        turbo=True,
        turbo_st=3500,
    )

    print(token)

# python -m pip install crapsolver-python==0.0.4