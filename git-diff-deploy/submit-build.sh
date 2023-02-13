#!/usr/bin/env bash
# Copyright 2023 Google. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#   agreement with Google.
# TODO run from the foot of the git directory
COMPOSER_NAME=example-environment
GCP_REGION=us-central1

gcloud builds submit --config=git-diff-deploy/cloud-build.yaml \
    --substitutions=_COMPOSER_NAME="${COMPOSER_NAME}",_GCP_REGION="${GCP_REGION}"

