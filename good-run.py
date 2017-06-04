#!/usr/bin/env python3

import os
from pathlib import Path
import pwd
import tempfile
import time
import shutil
from signal import SIGINT
import subprocess
from subprocess import PIPE
import sys


MAHIMAHI_RECORD_DIR = "record"
WPR_RECORD_FILE = "record.wpr"
DELAY = 100
TRACE = "5Mbps_trace"
BW = "5Mbit/s"
MEASURE_DIR = "measurements-%d-%s" % (DELAY, TRACE)
RUNS = 25
TIMEOUT = 150 # seconds

SHELLS = ["mm-delay", str(DELAY), "mm-link", TRACE, TRACE, "--"]


def cleanup_all():
    try:  # Try to clean up.
        os.system("killall chromedriver 2>/dev/null")
        os.system("killall chrome 2>/dev/null")
        os.system("(yes | sudo ipfw flush) >/dev/null 2>/dev/null")
    except Exception:
        pass


def run(args, cwd=None):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            preexec_fn=demote, cwd=cwd)
    try:
        outs, errs = proc.communicate(timeout=TIMEOUT)
        if proc.returncode != 0:
            raise Exception(errs)

        return outs
    except subprocess.TimeoutExpired:
        proc.terminate()
        raise


def atomic_write(content, filename):
    # https://stackoverflow.com/questions/2333872/atomic-writing-to-file-with-python
    tf = tempfile.NamedTemporaryFile(mode='w', delete=False)
    tf.write(content)
    tf.flush()
    os.fsync(tf.fileno())
    tf.close()
    os.rename(tf.name, filename)


def record_wpr(website):
    wpr_record_file = Path(WPR_RECORD_FILE)
    if wpr_record_file.exists():
        wpr_record_file.unlink()

    wpr_command = ["./replay.py", "-l", "critical", "--no-dns_forwarding", "--record",
            os.path.join(os.getcwd(), WPR_RECORD_FILE)]
    proc = subprocess.Popen(wpr_command, cwd="web-page-replay")
    try:
        time.sleep(2)
        run(["./chrome-fetch-host-resolver.py", website])
        time.sleep(2)
    finally:
        proc.send_signal(SIGINT)
        proc.wait(timeout=2)

    if proc.returncode != 0:
        raise Exception(errs)


def measure_wpr(website):
    wpr_record_file = Path(WPR_RECORD_FILE)
    if not wpr_record_file.exists():
        raise FileNotFoundError(WPR_RECORD_FILE)

    wpr_command = ["./replay.py", "-l", "critical", "--up", BW, "--down", BW,
            "--delay_ms=%d" % (2*DELAY), os.path.join(os.getcwd(), WPR_RECORD_FILE)]
    proc = subprocess.Popen(wpr_command, cwd="web-page-replay")
    try:
        time.sleep(2)
        measure = int(run(["./measure.py", website]))
        time.sleep(1)
    finally:
        proc.send_signal(SIGINT)
        proc.wait(timeout=2)

    if proc.returncode != 0:
        raise Exception(errs)

    return measure


def get_mahimahi_raws(website):
    print("Mahimahi raw...", file=sys.stderr)
    sys.stderr.flush()

    mahimahi_raws = []
    for i in range(RUNS):
        print(i, file=sys.stderr)
        sys.stderr.flush()

        while True:
            try:
                mahimahi_raw = int(run(SHELLS + ["./measure.py", website]))
                break
            except Exception:
                print("retrying...", file=sys.stderr)
                sys.stderr.flush()
            finally:
                cleanup_all()
        mahimahi_raws.append(mahimahi_raw)
    return mahimahi_raws


def mahimahi_record(website):
    print("Mahimahi recording...", file=sys.stderr)
    sys.stderr.flush()
    while True:
        try:
            if Path(MAHIMAHI_RECORD_DIR).exists():
                shutil.rmtree(MAHIMAHI_RECORD_DIR)
            run(["mm-webrecord", MAHIMAHI_RECORD_DIR, "./chrome-fetch.py", website])
            break
        except Exception:
            print("retrying...", file=sys.stderr)
            sys.stderr.flush()
        finally:
            cleanup_all()


def wpr_record(website):
    print("WPR recording...", file=sys.stderr)
    sys.stderr.flush()
    while True:
        try:
            record_wpr(website)
            break
        except Exception:
            print("retrying...", file=sys.stderr)
            sys.stderr.flush()
        finally:
            cleanup_all()


def get_wpr_raws(website):
    print("WPR raw...", file=sys.stderr)
    sys.stderr.flush()
    wpr_raws = []
    for i in range(RUNS):
        print(i, file=sys.stderr)
        sys.stderr.flush()
        while True:
            try:
                wpr_raw = int(run(["./shaped-measure.py", website,
                    str(DELAY*2), BW], cwd="web-page-replay"))
                break
            except Exception:
                print("retrying...", file=sys.stderr)
                sys.stderr.flush()
            finally:
                cleanup_all()
        wpr_raws.append(wpr_raw)
    return wpr_raws


def get_mahimahi_multis(website):
    print("Mahimahi multi...", file=sys.stderr)
    sys.stderr.flush()
    multis = []
    for i in range(RUNS):
        print(i, file=sys.stderr)
        sys.stderr.flush()
        while True:
            try:
                multi_measure = int(run(["mm-webreplay", MAHIMAHI_RECORD_DIR] + SHELLS + ["./measure.py", website]))
                break
            except Exception:
                print("retrying...", file=sys.stderr)
                sys.stderr.flush()
            finally:
                cleanup_all()
        multis.append(multi_measure)
    return multis


def get_mahimahi_singles(website):
    print("Mahimahi single...", file=sys.stderr)
    sys.stderr.flush()
    singles = []
    for i in range(RUNS):
        print(i, file=sys.stderr)
        sys.stderr.flush()
        while True:
            try:
                single_measure = int(run(["mm-webreplay", "--single-server",
                    MAHIMAHI_RECORD_DIR] + SHELLS + ["./measure.py", website]))
                break
            except Exception:
                print("retrying...", file=sys.stderr)
                sys.stderr.flush()
            finally:
                cleanup_all()
        singles.append(single_measure)
    return singles


def get_wpr_measures(website):
    print("WPR measure...", file=sys.stderr)
    sys.stderr.flush()
    wprs = []
    for i in range(RUNS):
        print(i, file=sys.stderr)
        sys.stderr.flush()
        while True:
            try:
                wpr_measure = measure_wpr(website)
                break
            except Exception:
                print("retrying...", file=sys.stderr)
                sys.stderr.flush()
            finally:
                cleanup_all()
        wprs.append(wpr_measure)
    return wprs


def print_list(l, file):
    print(','.join(map(str, l)), file=file)


def measure(website):
    print("Measuring %s" % website, file=sys.stderr)
    sys.stderr.flush()

    mahimahi_raws = get_mahimahi_raws(website)
    wpr_raws = get_wpr_raws(website)

    mahimahi_record(website)
    wpr_record(website)

    mahimahi_multis = get_mahimahi_multis(website)
    mahimahi_singles = get_mahimahi_singles(website)
    wprs = get_wpr_measures(website)

    filename = "%s.csv" % website
    result_dir = Path(sys.argv[2])
    if not result_dir.exists():
        result_dir.mkdir()

    with open(os.path.join(sys.argv[2], filename), "w") as f:
        print(website, file=f)
        print_list(mahimahi_raws, file=f)
        print_list(wpr_raws, file=f)
        print_list(mahimahi_multis, file=f)
        print_list(mahimahi_singles, file=f)
        print_list(wprs, file=f)


def main():
    print("DELAY = %d, TRACE = %s" % (DELAY, TRACE), file=sys.stderr)
    print(file=sys.stderr)
    sys.stderr.flush()
    cleanup_all()

    for website in sys.stdin:
        website = website.strip()
        if not website: break
        measure(website)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: ./run.py user")

    try:
        pw_record = pwd.getpwnam(sys.argv[1])
    except KeyError:
        sys.exit("User %s doesn't exist", sys.argv[1])

    def demote():
        user_uid = pw_record.pw_uid
        user_gid = pw_record.pw_gid
        os.setgid(user_gid)
        os.setuid(user_uid)

    main()
    print("DONE!", file=sys.stderr)
    sys.stderr.flush()
