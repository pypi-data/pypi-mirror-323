# Copyright ZettaBlock Labs 2024
import typer
import pyarrow.parquet as pq
import json
import pyarrow as pa
import os

from zetta._utils.async_utils import synchronizer
from zetta.cli.utils import (
    register_dataset_v2_to_neo,
    S3_REGION,
    list_parquet_files,
    get_catalog,
    list_datasets_v2_from_neo,
    upload_s3_by_presigned_url,
    get_tmp_token,
)

datasetsv2_cli = typer.Typer(
    name="datasetsv2",
    help="Manage your datasets in Zetta AI Network v2.",
    no_args_is_help=True,
)

SERVICE_CREATE_DATASET_URL = "https://neo-dev.prod.zettablock.com/v1/api/asset"
SERVICE_GITEA_URL = "https://gitea.stag-vxzy.zettablock.com"


@datasetsv2_cli.command(name="create", help="create dataset from parquet files")
@synchronizer.create_blocking
async def create(
    name: str = typer.Option("", help="Name of the dataset or table"),
    path: str = typer.Option("", help="Path of the dataset"),
    database: str = typer.Option("", help="Database of the dataset"),
    region: str = typer.Option(S3_REGION, help="region"),
):
    if not name:
        raise Exception("name is required")
    if not path:
        raise Exception("path is required")

    dataset = name
    print("Upload parquets from {} to {}".format(path, name))
    s3_file_lst = []
    # list parquet files
    parquet_files = list_parquet_files(path)
    for parquet_file, file_name in parquet_files:
        s3_path = upload_s3_by_presigned_url(
            parquet_file, "{}/{}".format(dataset, file_name)
        )
        print(s3_path)
        if s3_path:
            s3_file_lst.append(s3_path)
    print("uploaded s3 files:", s3_file_lst)
    if len(s3_file_lst) == 0:
        raise Exception("no parquet files uploaded")

    try:
        schema_json = get_schema_json(pq.read_schema(parquet_files[0][0]))
    except Exception as e:
        raise Exception("failed to get schema json:", e)

    num_rows = 0
    file_size = 0
    try:
        for parquet_file, file_name in parquet_files:
            table = pq.read_table(parquet_file)
            num_rows += table.num_rows
            file_size += os.path.getsize(parquet_file)
    except Exception as e:
        raise Exception("failed to get rows or size from parquet:", e)

    print(num_rows)
    print(file_size)

    try:
        register_dataset_v2_to_neo(
            {
                "name": dataset,
                "database": database,
                "region": region,
                "bucket": s3_file_lst[0].replace("s3://", "").split("/")[0],
                "location": ",".join(s3_file_lst),
                "file_paths": s3_file_lst,
                "metadata": json.dumps(schema_json),
                "size": file_size,
                "rows": num_rows,
            }
        )
    except Exception as e:
        raise Exception("failed to create dataset to Neo:", e)


def get_schema_json(schema: pa.Schema) -> str:
    def field_to_dict(field: pa.Field) -> dict:
        field_dict = {"type": str(field.type).upper()}

        if pa.types.is_list(field.type):
            field_dict["type"] = "LIST"
            field_dict["element"] = field_to_dict(field.type.value_field)
        elif pa.types.is_map(field.type):
            field_dict["type"] = "MAP"
            field_dict["key"] = {"type": str(field.type.key_field.type).upper()}
            field_dict["value"] = field_to_dict(field.type.item_field)
        elif pa.types.is_struct(field.type):
            field_dict["type"] = "STRUCT"
            field_dict["fields"] = {sub_field.name: field_to_dict(sub_field) for sub_field in field.type}
        elif pa.types.is_decimal(field.type):
            field_dict["type"] = "DECIMAL"
            field_dict["precision"] = field.type.precision
            field_dict["scale"] = field.type.scale

        return field_dict

    schema_dict = {field.name: field_to_dict(field) for field in schema}
    print(schema_dict)
    return schema_dict


@datasetsv2_cli.command(name="ls", help="list dataset(s)")
@synchronizer.create_blocking
async def ls(id: str = typer.Option("", help="id of the dataset")):
    list_datasets_v2_from_neo(id)


@datasetsv2_cli.command(name="read", help="read dataset to pandas")
@synchronizer.create_blocking
async def read(
    database: str = typer.Option("", help="Name of database"),
    namespace: str = typer.Option("", help="Name of the dataset namespace"),
    dataset: str = typer.Option("", help="Name of the dataset"),
    limit: int = typer.Option(10, help="Limit of the data to read"),
):
    if not database:
        raise Exception("database is required")
    if not namespace:
        raise Exception("namespace is required")
    if not dataset:
        raise Exception("dataset is required")
    print("read {} {}.{} limit = {}".format(database, namespace, dataset, limit))
    token_j = get_tmp_token(database)
    catalog = get_catalog(token_j)
    rows = (
        catalog.load_table("{}.{}".format(namespace, dataset))
        .scan(limit=limit)
        .to_pandas()
    )
    print(rows)


@datasetsv2_cli.command(name="save", help="save dataset to local parquet files")
@synchronizer.create_blocking
async def save(
    database: str = typer.Option("", help="Name of database"),
    namespace: str = typer.Option("", help="Name of the dataset namespace"),
    dataset: str = typer.Option("", help="Name of the dataset"),
    limit: int = typer.Option(-1, help="Limit of the data to read"),
):
    if not database:
        raise Exception("database is required")
    if not namespace:
        raise Exception("namespace is required")
    if not dataset:
        raise Exception("dataset is required")
    if limit <= 0:
        limit = None
    print(
        "save {} rows of {} {}.{}".format(
            "all" if limit is None else limit, database, namespace, dataset
        )
    )
    token_j = get_tmp_token(database)
    catalog = get_catalog(token_j)
    rows = (
        catalog.load_table("{}.{}".format(namespace, dataset))
        .scan(limit=limit)
        .to_pandas()
    )
    table = pa.Table.from_pandas(rows)
    pq.write_table(table, "{}-{}.parquet".format(namespace, dataset))
