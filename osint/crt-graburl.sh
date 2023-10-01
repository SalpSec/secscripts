#!/usr/bin/env bash
set -e

TARGET="$1"
OUTPUT_FILE=${2:-"$1.log"}

if [[ -z "$TARGET" ]]; then
	echo "Usage: crt-graburl.sh <url> (<output file>)"
	exit -1
fi

echo "Grabbing all CN's for $TARGET from crt.sh and writing to $OUTPUT_FILE"
curl -s -H "Accept: application/json" "https://crt.sh/\?q=${TARGET}" | jq '.[] | "\(.name_value)\n\(.common_name)"' | sed 's/\"//g' | sed 's/\\n/\n/g' | grep -e ".*${TARGET}" | sort | uniq > $OUTPUT_FILE
