"""Configuration for the locator."""
from __future__ import annotations

import os


# AWS
# UsageOperation is the AWS method for tagging an image with a billing code.
# RunInstances:0010 is for hourly images (customer pays cloud provider)
# RunInstances:0000 is for cloud access images (customer gets sub from Red Hat)
AWS_HOURLY_BILLING_CODE = "RunInstances:0010"
AWS_CLOUD_ACCESS_BILLING_CODE = "RunInstances:0000"
# RHEL's OwnerId for RHEL images in AWS is 309956199498.
AWS_RHEL_OWNER_ID = "309956199498"

# AZURE AUTHENTICATION
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID", None)
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET", None)
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID", None)
AZURE_SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID", None)
