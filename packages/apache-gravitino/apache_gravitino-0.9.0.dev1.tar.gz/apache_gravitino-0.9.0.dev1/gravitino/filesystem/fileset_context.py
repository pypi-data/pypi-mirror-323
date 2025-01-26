# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import os
import re
from typing import Optional
from google.cloud import storage
from gravitino import GravitinoClient, NameIdentifier, FilesetChange


class FilesetContext:

    gravitino_uri: str = None
    gravitino_metalake_name: str = None
    gravitino_client: GravitinoClient = None
    ident_pattern = re.compile("gvfs://fileset/([^/]+)/([^/]+)/([^/]+)(?:/[^/]+)*/?$")

    @classmethod
    def init(cls, uri: str, metalake_name: str):
        cls.gravitino_uri = uri
        cls.gravitino_metalake_name = metalake_name
        cls.gravitino_client = GravitinoClient(
            uri=cls.gravitino_uri, metalake_name=cls.gravitino_metalake_name
        )

    @classmethod
    def get_fileset_path(cls, original_path: str = None, auto_create: bool = True):
        # assuming the original path is "gcs:///app/michelangelo_v2/workspaces_0b/project_1/
        # workspaces/pipeline_run_uuid_1/operators/operator_1/tmp"
        return "gvfs://fileset/infra/ma/project_1-pipeline_run_uuid_1-operator_1/tmp"

    @classmethod
    def sync(
        cls,
        fileset_path: str,
        src_location: Optional[str] = None,
        dest_location: Optional[str] = None,
    ):
        match = cls.ident_pattern.match(fileset_path)
        if not match:
            raise ValueError(f"Invalid fileset path: {fileset_path}")

        catalog_name = match.group(1)
        schema_name = match.group(2)
        fileset_name = match.group(3)
        catalog = cls.gravitino_client.load_catalog(catalog_name)
        fileset = catalog.as_fileset_catalog().load_fileset(
            NameIdentifier.of(schema_name, fileset_name)
        )
        properties = fileset.properties()

        # Figure out the source and destination locations
        src_location = src_location if src_location else properties["primary_location"]
        dest_location = (
            dest_location
            if dest_location
            else cls._get_secondary_location(src_location)
        )

        # call gcs API to sync two buckets
        src_storage_location = properties[f"location-{src_location}"]
        dest_storage_location = properties[f"location-{dest_location}"]
        if src_storage_location is None or dest_storage_location is None:
            raise ValueError(
                f"Invalid storage location: {src_storage_location}, {dest_storage_location}"
            )

        # Update the status to in-sync.
        catalog.as_fileset_catalog().alter_fileset(
            NameIdentifier.of(schema_name, fileset_name),
            FilesetChange.set_property(f"status-{dest_location}", "in-sync"),
        )

        # sync the two storage locations
        cls.copy_folder(src_storage_location, dest_storage_location)

        # Update the status to latest
        catalog.as_fileset_catalog().alter_fileset(
            NameIdentifier.of(schema_name, fileset_name),
            FilesetChange.set_property(f"status-{dest_location}", "latest"),
        )

    @classmethod
    def get_sync_status(cls, fileset_path: str, location: Optional[str] = None) -> str:
        match = cls.ident_pattern.match(fileset_path)
        if not match:
            raise ValueError(f"Invalid fileset path: {fileset_path}")

        catalog_name = match.group(1)
        schema_name = match.group(2)
        fileset_name = match.group(3)
        catalog = cls.gravitino_client.load_catalog(catalog_name)
        fileset = catalog.as_fileset_catalog().load_fileset(schema_name, fileset_name)
        properties = fileset.properties()

        location = (
            location
            if location
            else cls._get_secondary_location(properties["primary_location"])
        )
        return properties[f"status-{location}"]

    @classmethod
    def copy_folder(cls, src_path: str, dest_path: str):
        account_file = os.environ["SERVICE_ACCOUNT_FILE"]
        if account_file is None:
            raise ValueError("SERVICE_ACCOUNT_FILE environment variable is not set.")
        if not os.path.exists(account_file):
            raise ValueError(f"Service account file does not exist: {account_file}")

        storage_client = storage.Client.from_service_account_json(account_file)

        # Get the source bucket name from the src_path like "gs://bucket_name/folder1/folder2"
        src_bucket_name = src_path.split("/")[2]
        src_path = "/".join(src_path.split("/")[3:])
        src_bucket = storage_client.get_bucket(src_bucket_name)

        # Get the destination bucket name from the dest_path like "gs://bucket_name/folder1/folder2"
        dest_bucket_name = dest_path.split("/")[2]
        dest_path = "/".join(dest_path.split("/")[3:])
        dest_bucket = storage_client.get_bucket(dest_bucket_name)

        # List all the blobs in the source bucket
        blobs = list(src_bucket.list_blobs(prefix=src_path))
        for blob in blobs:
            # Copy the blob to the destination bucket
            new_blob_name = dest_path + blob.name[len(src_path) :]
            new_blob = src_bucket.copy_blob(blob, dest_bucket, new_blob_name)
            print(f"Blob {blob.name} has been copied to {new_blob.name}")

    @classmethod
    def _get_secondary_location(cls, src_location: str) -> str:
        if src_location.lower() == "dca":
            return "dcacld"
        if src_location.lower() == "dcacld":
            return "dca"
        if src_location.lower() == "phx":
            return "phxcld"
        if src_location.lower() == "phxcld":
            return "phx"

        raise ValueError(f"Unknown location: {src_location}")
