#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: pylint_sample.sh <target>"
fi

tgt=${1}

files=`find ${tgt} -name "*.py"`
ignores=("sample_2_7/__init__.py")

# pylint
for file in ${files[@]}; do
    # ignore file in ignores
    found=0
    for ign in ${ignores[@]}; do
        if [ `echo "${file}" | grep "${ign}"` ]; then
            found=1
        fi
    done
    if [ ${found} -eq 1 ]; then
        continue
    fi
    echo "======= pylint test "${file}" ======="
    pylint ${file}
    ret=`echo $?`
    if [ ${ret} -ne 0 ]; then
        echo "Test failed (error code: "${ret}")"
        exit 1
    fi
done

# pep8
for file in ${files[@]}; do
    # ignore file in ignores
    found=0
    for ign in ${ignores[@]}; do
        if [ `echo "${file}" | grep "${ign}"` ]; then
            found=1
        fi
    done
    if [ ${found} -eq 1 ]; then
        continue
    fi
    echo "======= pep8 test "${file}" ======="
    pep8 ${file}
    ret=`echo $?`
    if [ ${ret} -ne 0 ]; then
        exit 1
    fi
done
