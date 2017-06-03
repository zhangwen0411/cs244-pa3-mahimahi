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
MEASURE_DIR = "measurements-%d-%s" % (DELAY, TRACE)
RUNS = 25
TIMEOUT = 180 # seconds
RETRIES = 3

SHELLS = ["mm-delay", str(DELAY), "mm-link", TRACE, TRACE, "--"]


def run(args):
    try:  # Try to clean up.
        subprocess.run(["killall", "chromedriver"], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, timeout=2)
        subprocess.run(["killall", "chrome"], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, timeout=2)
    except Exception:
        pass

    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            preexec_fn=demote)
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

    wpr_command = ["./replay.py", "--no-dns_forwarding", "--record",
            os.path.join(os.getcwd(), WPR_RECORD_FILE)]
    proc = subprocess.Popen(wpr_command, cwd="web-page-replay") #, stdout=PIPE, stderr=PIPE)
    try:
        time.sleep(2)
        run(["./chrome-fetch-host-resolver.py", website])
        time.sleep(2)
    finally:
        proc.send_signal(SIGINT)
        _, errs = proc.communicate(timeout=2)

    if proc.returncode != 0:
        raise Exception(errs)


def measure_wpr(website):
    wpr_record_file = Path(WPR_RECORD_FILE)
    if not wpr_record_file.exists():
        raise FileNotFoundError(WPR_RECORD_FILE)

    wpr_command = ["./replay.py", os.path.join(os.getcwd(), WPR_RECORD_FILE)]
    proc = subprocess.Popen(wpr_command, cwd="web-page-replay", stdout=PIPE,
            stderr=PIPE)
    try:
        time.sleep(2)
        measure = int(run(SHELLS + ["./measure.py", website]))
        time.sleep(1)
    finally:
        proc.send_signal(SIGINT)
        _, errs = proc.communicate(timeout=2)

    if proc.returncode != 0:
        raise Exception(errs)

    return measure


def dot():
    sys.stderr.write(".")
    sys.stderr.flush()


def measure(website, result_path):
    print("Measuring %s" % website, file=sys.stderr)

    for i in range(RUNS):
        sys.stderr.write("\tRun %d " % i)
        sys.stderr.flush()
        result_file = result_path / ('%s-%d' % (website, i))
        if result_file.exists():
            print("EXISTS", file=sys.stderr)
            continue

        success = False
        for _ in range(RETRIES):
            try:
                raw_raw_measure = int(run(["./measure.py", website]))
                dot()

                record_wpr(website)
                dot()

                wpr_measure = measure_wpr(website)
                dot()

                print(raw_raw_measure, wpr_measure)

                success = True
                sys.exit(0)

                start_time = time.perf_counter()
                raw_measure = int(run(SHELLS + ["./measure.py", website]))
                dot()

                if Path(MAHIMAHI_RECORD_DIR).exists():
                    shutil.rmtree(MAHIMAHI_RECORD_DIR)
                run("mm-webrecord", MAHIMAHI_RECORD_DIR, "./chrome-fetch.py", website)
                dot()

                multi_measure = int(run(["mm-webreplay", MAHIMAHI_RECORD_DIR] +
                    SHELLS + ["./measure.py", website]))
                dot()

                single_measure = int(run(["mm-webreplay", "--single-server",
                    MAHIMAHI_RECORD_DIR] + SHELLS + ["./measure.py", website]))
                dot()

                atomic_write("%d,%d,%d" % (raw_measure, multi_measure,
                    single_measure), str(result_file))
                end_time = time.perf_counter()

                print(" {0}".format(end_time - start_time), file=sys.stderr)

                success = True
                break
            except Exception as e:
                print(e, "retrying", file=sys.stderr)

        if not success:
            print("Giving up on %s..." % website, file=sys.stderr)
            return


def main():
    print("DELAY = %d, TRACE = %s" % (DELAY, TRACE), file=sys.stderr)
    print(file=sys.stderr)

    result_path = Path(MEASURE_DIR)
    if not result_path.exists():
        result_path.mkdir()
    for website in sys.stdin:
        website = website.strip()
        measure(website, result_path)


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
