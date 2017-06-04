#!/usr/bin/env python

import sys

from selenium import webdriver

from my_trafficshaper import TrafficShaper


def measure(url):
    """
    Loads URL in Chrome and returns page load time in milliseconds.

    Page load time is defined as the time elapsed between navigationStart and
    loadEventEnd.
    """
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "http://" + url
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    wd = webdriver.Chrome(chrome_options=options)
    try:
        wd.get(url)
        loadTime = wd.execute_script("return (window.performance.timing.loadEventEnd - \
                window.performance.timing.navigationStart)")
        return loadTime
    finally:
        wd.quit()


def main():
    url = sys.argv[1]
    delay = sys.argv[2]
    bw = sys.argv[3]

    with TrafficShaper(up_bandwidth=bw, down_bandwidth=bw, delay_ms=delay):
        print measure(url.decode('utf-8'))


if __name__ == "__main__":
    main()
