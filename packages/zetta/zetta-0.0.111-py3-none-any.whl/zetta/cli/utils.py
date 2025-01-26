# Copyright ZettaBlock Labs 2024
import os
from pyiceberg.catalog import load_catalog
import configparser
import requests
import re

ICEBERG_DATA_LOCATION = "s3://ai-network-worker-demo/iceberg-data/"
S3_BUCKET = "ai-network-worker-demo"
S3_REGION = "us-east-1"
AWS_DATA_CATALOG = "AwsDataCatalog"
NEO_DEV_URL = "https://neo-dev.prod.zettablock.com/v1/api"
CREATE_DATASET_NEO_URL = "{}/dataset/create".format(NEO_DEV_URL)


def list_parquet_files(path_str):
    files = []
    for file in os.listdir(path_str):
        if file.endswith(".parquet"):
            files.append((os.path.join(path_str, file), file))
    return files


def upload_s3_by_presigned_url(parquet_file, obj):
    url = get_presigned_url(obj)
    with open(parquet_file, "rb") as f:
        http_response = requests.put(url, data=f)
    if 200 != http_response.status_code:
        return ""
    try:
        s3_url = url.split("?")[0].replace("https", "s3")
        s3_url = re.sub(r"\.s3\S+amazonaws\.com", "", s3_url)
        return s3_url
    except Exception as e:
        print("failed to get json: {}".format(e))
        return ""


def get_catalog(j):
    catalog = load_catalog(
        AWS_DATA_CATALOG,
        **{
            "type": "glue",
            "region": S3_REGION,
            # "py-io-impl": "pyiceberg.io.pyarrow.PyArrowFileIO",
            "glue.access-key-id": j["AccessKeyId"],
            "glue.secret-access-key": j["SecretAccessKey"],
            "glue.session-token": j["SessionToken"],
            "s3.access-key-id": j["AccessKeyId"],
            "s3.secret-access-key": j["SecretAccessKey"],
            "s3.session-token": j["SessionToken"],
        },
    )

    return catalog


def register_dataset_v2_to_neo(j):
    """
    {
        "subnet":"testdb",
        "name": "testtable",
        "region": "us",
        "bucket": "testbucket",
        "namespace": "table namespace",
        "metadata": "json string",
        "location": "file location",
        "file_paths":["hoho"],
        "size":999
    }
    """
    try:
        zetta_root = os.path.expanduser("~")
        secrets_path = os.path.join(zetta_root, ".zetta/secrets")
        config = configparser.ConfigParser()
        config.read(secrets_path)
        api_key = config.get("default", "api_key", fallback=None)
    except FileNotFoundError:
        raise Exception(f"File not found: {secrets_path}")
    except IOError:
        raise Exception(f"An error occurred while reading the file: {secrets_path}")

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
    }

    json_data = j
    try:
        response = requests.post(
            CREATE_DATASET_NEO_URL, headers=headers, json=json_data
        )
    except Exception as e:
        print(response.status_code, response.text)
        raise Exception(f"Failed to create dataset to Neo: {e}")

    if response.status_code == 200:
        print(f"Successfully created dataset {response.json()}")
    else:
        response.raise_for_status()


def list_datasets_v2_from_neo(dataset_id: str):
    try:
        zetta_root = os.path.expanduser("~")
        secrets_path = os.path.join(zetta_root, ".zetta/secrets")
        config = configparser.ConfigParser()
        config.read(secrets_path)
        api_key = config.get("default", "api_key", fallback=None)
    except FileNotFoundError:
        raise Exception(f"File not found: {secrets_path}")
    except IOError:
        raise Exception(f"An error occurred while reading the file: {secrets_path}")

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
    }
    if dataset_id:
        url = "{}/dataset/get?id={}".format(NEO_DEV_URL, dataset_id)
    else:
        url = "{}/dataset/list".format(NEO_DEV_URL)
    response = requests.request("GET", url, headers=headers)

    print(response.text)


def list_databases_v2_from_neo():
    try:
        zetta_root = os.path.expanduser("~")
        secrets_path = os.path.join(zetta_root, ".zetta/secrets")
        config = configparser.ConfigParser()
        config.read(secrets_path)
        api_key = config.get("default", "api_key", fallback=None)
    except FileNotFoundError:
        raise Exception(f"File not found: {secrets_path}")
    except IOError:
        raise Exception(f"An error occurred while reading the file: {secrets_path}")

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
    }

    url = "{}/database/list".format(NEO_DEV_URL)
    response = requests.request("GET", url, headers=headers)

    print(response.text)


def get_database_v2_from_neo_by_name(name):
    try:
        zetta_root = os.path.expanduser("~")
        secrets_path = os.path.join(zetta_root, ".zetta/secrets")
        config = configparser.ConfigParser()
        config.read(secrets_path)
        api_key = config.get("default", "api_key", fallback=None)
    except FileNotFoundError:
        raise Exception(f"File not found: {secrets_path}")
    except IOError:
        raise Exception(f"An error occurred while reading the file: {secrets_path}")

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
    }

    url = "{}/database/get?name={}".format(NEO_DEV_URL, name)
    response = requests.request("GET", url, headers=headers)

    print(response.text)


def get_presigned_url(obj: str, expiration: int = 600):
    try:
        zetta_root = os.path.expanduser("~")
        secrets_path = os.path.join(zetta_root, ".zetta/secrets")
        config = configparser.ConfigParser()
        config.read(secrets_path)
        api_key = config.get("default", "api_key", fallback=None)
    except FileNotFoundError:
        raise Exception(f"File not found: {secrets_path}")
    except IOError:
        raise Exception(f"An error occurred while reading the file: {secrets_path}")

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
    }

    url = "{}/dataset/url/upload?obj={}&ttl={}".format(NEO_DEV_URL, obj, expiration)

    try:
        response = requests.request("GET", url, headers=headers)
    except Exception as e:
        raise Exception(f"Failed to get presigned url: {e}")

    if response.status_code != 200:
        raise Exception(
            f"[{response.status_code}] Failed to get presigned url: {response.text}"
        )

    return response.json()["data"]


def get_tmp_token(database: str):
    try:
        zetta_root = os.path.expanduser("~")
        secrets_path = os.path.join(zetta_root, ".zetta/secrets")
        config = configparser.ConfigParser()
        config.read(secrets_path)
        api_key = config.get("default", "api_key", fallback=None)
    except FileNotFoundError:
        raise Exception(f"File not found: {secrets_path}")
    except IOError:
        raise Exception(f"An error occurred while reading the file: {secrets_path}")

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
    }

    url = "{}/dataset/token?subnet={}".format(NEO_DEV_URL, database)

    try:
        response = requests.request("GET", url, headers=headers)
    except Exception as e:
        raise Exception(f"Failed to tmp token: {e}")

    if response.status_code != 200:
        raise Exception(
            f"[{response.status_code}] Failed to get tmp token: {response.text}"
        )

    return response.json()["data"]
