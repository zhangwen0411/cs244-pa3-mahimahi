#!/usr/bin/env python3

import os
from pathlib import Path
import tempfile
import time
import shutil
import subprocess
import sys


RECORD_DIR = "record"
DELAY = 100
TRACE = "5Mbps_trace"
MEASURE_DIR = "measurements-%d-%s" % (DELAY, TRACE)
RUNS = 25
TIMEOUT = 180 # seconds
RETRIES = 3

SHELLS = ["mm-delay", str(DELAY), "mm-link", TRACE, TRACE, "--"]


def run(*args):
    try:  # Try to clean up.
        subprocess.run(["killall", "chromedriver"], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, timeout=2)
        subprocess.run(["killall", "chrome"], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, timeout=2)
    except Exception:
        pass

    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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


def measure(website, result_path):
    print("Measuring %s" % website, file=sys.stderr)

    for i in range(RUNS):
        sys.stderr.write("\tRun %d " % i)
        result_file = result_path / ('%s-%d' % (website, i))
        if result_file.exists():
            print("EXISTS", file=sys.stderr)
            continue
        sys.stderr.flush()

        success = False
        for _ in range(RETRIES):
            try:
                start_time = time.perf_counter()
                raw_measure = int(run(*SHELLS, "./measure.py", website))
                sys.stderr.write(".")
                sys.stderr.flush()

                if Path(RECORD_DIR).exists():
                    shutil.rmtree(RECORD_DIR)
                run("mm-webrecord", RECORD_DIR, "./chrome-fetch.py", website)
                sys.stderr.write(".")
                sys.stderr.flush()

                multi_measure = int(run("mm-webreplay", RECORD_DIR, *SHELLS,
                    "./measure.py", website))
                sys.stderr.write(".")
                sys.stderr.flush()

                single_measure = int(run("mm-webreplay", "--single-server",
                    RECORD_DIR, *SHELLS, "./measure.py", website))
                sys.stderr.write(".")
                sys.stderr.flush()

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
    result_path.mkdir(exist_ok=True)
    for website in sys.stdin:
        website = website.strip()
        measure(website, result_path)


if __name__ == "__main__":
    main()
