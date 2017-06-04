#!/usr/bin/env python

"""
Usage: ./plot.py input_file output_file
"""

import csv
from collections import defaultdict
import sys

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

import numpy as np
import statsmodels.api as sm # recommended import according to the docs



def err(gold, seen):
    gold = float(gold)
    seen = float(seen)
    return abs(gold-seen)/gold*100


def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


def mean_line(f):
    return mean(map(float, f.readline().split(',')))


def stats():
    wpr_errs = []
    multi_errs = []
    single_errs = []

    with open(sys.argv[1], "r") as f:
        while True:
            website = f.readline()
            if not website.strip():
                break

            mahimahi_raw = mean_line(f)
            wpr_raw = mean_line(f)
            mahimahi_multi = mean_line(f)
            mahimahi_single = mean_line(f)
            wpr = mean_line(f)

            wpr_errs.append(err(wpr_raw, wpr))
            multi_errs.append(err(mahimahi_raw, mahimahi_multi))
            single_errs.append(err(mahimahi_raw, mahimahi_single))

    return { "wpr": wpr_errs, "multi": multi_errs, "single": single_errs }


def plot_ecdf(data, x, *args, **kwargs):
    ecdf = sm.distributions.ECDF(data)
    # x = np.linspace(0, XMAX)
    y = ecdf(x)
    # plt.step(x, y, *args, **kwargs)
    plt.plot(x, y, *args, drawstyle="steps-post", lw=1.0, **kwargs)


data = stats()
wpr = data["wpr"]
multi = data["multi"]
single = data["single"]

all_data = wpr + single + multi
xs = np.array(sorted(all_data))
plot_ecdf(multi, xs, "b-", label="ReplayShell, multi-server")
plot_ecdf(single, xs, "g--", label="ReplayShell, single-server")
plot_ecdf(wpr, xs, "r:", label="web-page-replay")

XMAX = 150

plt.xlim(0, XMAX)
plt.xticks(np.arange(0, XMAX+1, 30))
plt.xlabel("Absolute Value of Relative Percent Error")
plt.ylim(0, 1)
plt.yticks(np.arange(0, 1+.25, .25))
plt.ylabel("Cumulative Proportion")
plt.legend(loc='lower right')
plt.savefig(sys.argv[2])
