#!/usr/bin/env python3.10
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/benchmark/bench.py
# VERSION:     0.1.0
# CREATED:     2025-01-27 14:00
# AUTHOR:      Sitt Guruvanich <aekazitt+github@gmail.com>
# DESCRIPTION:
#
# HISTORY:
# *************************************************************

### Standard packages ###
import re  # noqa: D100
import time
from random import choices
from string import ascii_letters, digits

### Local modules ###
from aeque import (
    compile,
    escape,
    fmatch,
    findall,
    finditer,
    fullmatch,
    search,
    split,
    sub,
    subn,
)


def benchmark(func, *args, iterations=1000):  # noqa: D103
    start = time.time()
    for _ in range(iterations):
        func(*args)
    end = time.time()
    return (end - start) * 1000  # Convert to milliseconds

# Test cases
PATTERN = r'(\w+)\s+(\d+)'
TEXT = ''.join(choices(ascii_letters + digits, k=1000))
ITERATIONS = 100

if __name__ == "__main__":
    aeque_results = [
        ("Compile", benchmark(compile, PATTERN, iterations=ITERATIONS), True),
        ("Search", benchmark(search, compile(PATTERN), TEXT, iterations=ITERATIONS), True),
        ("Find Match", benchmark(fmatch, compile(PATTERN), TEXT, iterations=ITERATIONS), True),
        ("Full Match", benchmark(fullmatch, compile(PATTERN), TEXT, iterations=ITERATIONS), True),
        ("Split", benchmark(split, compile(PATTERN), TEXT, iterations=ITERATIONS), True),
        ("Find All", benchmark(findall, compile(PATTERN), TEXT, iterations=ITERATIONS), True),
        ("Find Iter", benchmark(finditer, compile(PATTERN), TEXT, iterations=ITERATIONS), True),
        ("Sub", benchmark(sub, compile(PATTERN), 'foo', TEXT, iterations=ITERATIONS), True),
        ("Subn", benchmark(subn, compile(PATTERN), 'foo', TEXT, iterations=ITERATIONS), True),
        ("Escape", benchmark(escape, TEXT, iterations=ITERATIONS), False)
    ]

    re_results = [
        ("Compile", benchmark(re.compile, PATTERN, iterations=ITERATIONS), True),
        ("Search", benchmark(lambda pattern: pattern.search(TEXT), re.compile(PATTERN), iterations=ITERATIONS), True),
        ("Find Match", benchmark(lambda pattern: pattern.match(TEXT), re.compile(PATTERN), iterations=ITERATIONS), True),
        ("Full Match", benchmark(lambda pattern: pattern.fullmatch(TEXT), re.compile(PATTERN), iterations=ITERATIONS), True),
        ("Split", benchmark(lambda pattern: pattern.split(TEXT), re.compile(PATTERN), iterations=ITERATIONS), True),
        ("Find All", benchmark(lambda pattern: pattern.findall(TEXT), re.compile(PATTERN), iterations=ITERATIONS), True),
        ("Find Iter", benchmark(lambda pattern: list(pattern.finditer(TEXT)), re.compile(PATTERN), iterations=ITERATIONS), True),
        ("Sub", benchmark(lambda pattern: pattern.sub('foo', TEXT), re.compile(PATTERN), iterations=ITERATIONS), True),
        ("Subn", benchmark(lambda pattern: pattern.subn('foo', TEXT), re.compile(PATTERN), iterations=ITERATIONS), True),
        ("Escape", benchmark(re.escape, TEXT, iterations=ITERATIONS), False)
    ]

    max_len = max(len(op) for op, _, _ in aeque_results + re_results)
    print(f"{'Operation':{max_len}} | {'aeque (ms)':<10} | {'re (ms)':<10} | {'Used Regex':<10} | {'Faster':<10}")
    print("-" * (max_len + 45))

    aeque_times = []
    re_times = []

    for (op, aeque_time, used_regex_aeque), (_, re_time, used_regex_re) in zip(aeque_results, re_results):
        used_regex = "Yes" if used_regex_aeque and used_regex_re else "No"
        faster = "aeque" if aeque_time < re_time else "re"
        print(f"{op:{max_len}} | {aeque_time:<10.5f} | {re_time:<10.5f} | {used_regex:<10} | {faster:<10}")
        aeque_times.append(aeque_time)
        re_times.append(re_time)

    mean_aeque = sum(aeque_times) / len(aeque_times)
    mean_re = sum(re_times) / len(re_times)
    performance_ratio = mean_re / mean_aeque

    print(f"\nThe aeque is {performance_ratio:.2f}x faster than re module on average")
