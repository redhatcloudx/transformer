#!/bin/bash
# az vm image list -f RHEL -l eastus --all > azure_list_images.json
gcloud config set account rhel-cloud
gcloud compute images list --format="json" > google_list_images.json

# Get images from one region and sort them by creation date.
# NOTE(mhayden): The sorting is nice because it reduces the size of the diffs
# when the image list is updated. 😉
aws --region=us-east-1 ec2 describe-images \
    --owner 309956199498 \
    --filter "Name=is-public,Values=true" | \
    jq '{ "Images": .Images | sort_by(.CreationDate)}' \
    > aws_list_images.json
