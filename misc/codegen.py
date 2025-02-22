#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re

CURL_GIT_PATH = os.environ.get("CURL_GIT_PATH", './curl')

target_dirs = [
    '{}/include/curl'.format(CURL_GIT_PATH),
    '/usr/local/include',
    'libdir/gcc/target/version/include'
    '/usr/target/include',
    '/usr/include',
]


def get_curl_path():
    for d in target_dirs:
        for root, dirs, files in os.walk(d):
            if 'curl.h' in files:
                return os.path.join(root, 'curl.h')
    raise Exception("Not found")


opts = []
deprecated_opts = []
codes = []
infos = []
auths = []

init_pattern = re.compile(
    r'CURLINIT\(([^,]+),'
)
opt_pattern = re.compile(
    r'CURLOPT\(CURLOPT_([^,]+),'
)
deprecated_pattern = re.compile(
    r'CURLOPTDEPRECATED\(CURLOPT_([^,]+),'
)
auth_pattern = re.compile(r'#define CURLAUTH_(\S+)')
error_pattern = re.compile(r'^\s+(CURLE_[A-Z_0-9]+),')
info_pattern = re.compile(r'^\s+(CURLINFO_[A-Z_0-9]+)\s+=')

with open(get_curl_path()) as f:
    for line in f:  # noqa: C901
        match = init_pattern.findall(line)
        if match:
            opts.append(match[0])
        match = opt_pattern.findall(line)
        if match:
            opts.append(match[0])
        if line.startswith('#define CURLOPT_'):
            o = line.split()
            opts.append(o[1][8:])
        match = deprecated_pattern.findall(line)
        if match:
            deprecated_opts.append(match[0])
        match = auth_pattern.findall(line)
        if match:
            auths.append(match[0])
        match = error_pattern.findall(line)
        if match:
            codes.append(match[0])
        if line.startswith('#define CURLE_'):
            c = line.split()
            codes.append(c[1])
        match = info_pattern.findall(line)
        if match:
            infos.append(match[0])
        if line.startswith('#define CURLINFO_'):
            i = line.split()
            if '0x' not in i[2]:  # :(
                infos.append(i[1])

template = """//go:generate /usr/bin/env python ./misc/codegen.py

package curl
/*
#include <curl/curl.h>
#include "compat.h"
*/
import "C"

// CURLcode
const (
{code_part}
)

// easy.Setopt(flag, ...)
const (
{opt_part}
)

// easy.Getinfo(flag)
const (
{info_part}
)

// Auth
const (
{auth_part}
)

// Deprecated stuff
const(
{deprecated_part}
)

// generated ends
"""

code_part = []
for c in codes:
    code_part.append("\t{:<25} = C.{}".format(c[4:], c))

code_part = '\n'.join(code_part)

deprecated_part = []
for o in deprecated_opts:
    deprecated_part.append("\tOPT_{0:<25} = C.CURLOPT_{0}".format(o))

deprecated_part = '\n'.join(deprecated_part)

opt_part = []
for o in opts:
    opt_part.append("\tOPT_{0:<25} = C.CURLOPT_{0}".format(o))

opt_part = '\n'.join(opt_part)

info_part = []
for i in infos:
    info_part.append("\t{:<25} = C.{}".format(i[4:], i))

info_part = '\n'.join(info_part)

auth_part = []
for a in auths:
    auth_part.append("\tAUTH_{0:<25} = C.CURLAUTH_{0} & (1<<32 - 1)".format(a))

auth_part = '\n'.join(auth_part)

with open('./const_gen.go', 'w') as fp:
    fp.write(template.format(**locals()))
