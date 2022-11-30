#!/bin/bash
# az vm image list -f RHEL -l eastus --all > azure_list_images.json
gcloud config set account rhel-cloud
gcloud compute images list --format="json" > google_list_images.json
aws --region=us-east-1 ec2 describe-images --owner 309956199498 --filter "Name=is-public,Values=true" > aws_list_images.json
