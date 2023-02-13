#!/usr/bin/env bash
# Copyright 2023 Google. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#   agreement with Google.
#
COMPOSER_NAME=example-environment
GCP_REGION=us-central1
PROJECT_NUMBER=
GCP_PROJECT=
SERVICE_ACCOUNT=composer-service-account@${GCP_PROJECT}.iam.gserviceaccount.com

gcloud projects add-iam-policy-binding ${SERVICE_ACCOUNT} \
    --member serviceAccount:service-${PROJECT_NUMBER}@cloudcomposer-accounts.iam.gserviceaccount.com \
    --role roles/composer.ServiceAgentV2Ext

gcloud composer environments create ${COMPOSER_NAME} \
    --location GCP_REGION \
    --image-version composer-2.1.5-airflow-2.4.3 \
    --service-account ${SERVICE_ACCOUNT} \
    --network=  \
    --subnetwork= \
    --enable-private-environment \
    --enable-private-endpoint \
    --web-server-allow-all

