#!/usr/bin/env bash
TARGET_HOST="$1"
TARGET_PATH="$2"

curl --request POST \
  --header 'Content-Type: application/json' \
  --url "https://${TARGET_HOST}/${TARGET_PATH}" \
  --data '{"query":"query { __schema{types{name,fields{name,args{name,description,type{name,kind,ofType{name, kind}}}}}} }"}' -o "graphql-${TARGET_HOST}.json"
