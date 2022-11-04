# AZURE_CLIENT_ID="" AZURE_CLIENT_SECRET="" AZURE_TENANT_ID="" AZURE_SUBSCRIPTION_ID="" python update_testdata.py

import os

import requests

from rhelocator import config
from rhelocator.update_images import azure


TESTDATA_DIRECTORY = "testdata"


def save_azure_image_responses():
    for publisher, offers in config.AZURE_RHEL_IMAGE_TREE.items():
        for offer, skus in offers.items():
            for sku, version in skus.items():
                access_token = azure.get_access_token()
                headers = {"Authorization": f"Bearer {access_token}"}
                params = {"api-version": "2022-08-01"}
                url = (
                    f"https://management.azure.com/subscriptions/{config.AZURE_SUBSCRIPTION_ID}/"
                    f"providers/Microsoft.Compute/locations/{config.AZURE_DEFAULT_LOCATION}/publishers/"
                    f"{publisher}/artifacttypes/vmimage/offers/{offer}/skus/{sku}/versions"
                )
                resp = requests.get(url, params=params, headers=headers, timeout=10)
                with open(
                    f"{TESTDATA_DIRECTORY}/azure_sku-{sku}_v-{version}.response", "wb"
                ) as f:
                    f.write(resp.content)


def main():
    if not os.path.exists(TESTDATA_DIRECTORY):
        os.makedirs(TESTDATA_DIRECTORY)
    save_azure_image_responses()


if __name__ == "__main__":
    main()
