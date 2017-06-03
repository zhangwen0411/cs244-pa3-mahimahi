#!/usr/bin/env python

import sys

from selenium import webdriver


def main():
    url = sys.argv[1]
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "http://" + url

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    wd = webdriver.Chrome(chrome_options=options)
    try:
        wd.get(url)
    finally:
        import time; time.sleep(3)
        wd.quit()


if __name__ == "__main__":
    main()
