#! /usr/bin/env bash
# Copyright 2023 Google. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#   agreement with Google.
set -oeu pipefail
# get bucket name
echo $COMPOSER_NAME, $GCP_REGION
BUCKET_NAME=$(gcloud composer environments describe ${COMPOSER_NAME} --location=${GCP_REGION} --format='get(config.dagGcsPrefix)')
echo $BUCKET_NAME
git diff main...${BRANCH_NAME} --name-only | grep "dags" > dagfilelist.txt
cat dagfilelist.txt
  while read p; do
    echo "file name: $p"
    gsutil cp $p $BUCKET_NAME/
  done < dagfilelist.txt
cat dagfilelist.txt