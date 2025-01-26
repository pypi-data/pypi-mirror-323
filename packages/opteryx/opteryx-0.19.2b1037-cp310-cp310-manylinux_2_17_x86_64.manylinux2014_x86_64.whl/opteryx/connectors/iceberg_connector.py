# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# See the License at http://www.apache.org/licenses/LICENSE-2.0
# Distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND.

"""
Arrow Reader

Used to read datasets registered using the register_arrow or register_df functions.
"""

import struct
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from typing import Union

import pyarrow
import pyiceberg.types
from orso.schema import FlatColumn
from orso.schema import RelationSchema

from opteryx.connectors import DiskConnector
from opteryx.connectors.base.base_connector import BaseConnector
from opteryx.connectors.capabilities import LimitPushable
from opteryx.connectors.capabilities import Statistics
from opteryx.models import RelationStatistics


class IcebergConnector(BaseConnector, LimitPushable, Statistics):
    __mode__ = "Blob"
    __type__ = "ICEBERG"

    def __init__(self, *args, catalog=None, io=DiskConnector, **kwargs):
        BaseConnector.__init__(self, **kwargs)
        LimitPushable.__init__(self, **kwargs)
        Statistics.__init__(self, **kwargs)

        self.dataset = self.dataset.lower()
        self.table = catalog.load_table(self.dataset)
        self.io_connector = io(**kwargs)

    def get_dataset_schema(self) -> RelationSchema:
        iceberg_schema = self.table.schema()
        arrow_schema = iceberg_schema.as_arrow()

        self.schema = RelationSchema(
            name=self.dataset,
            columns=[FlatColumn.from_arrow(field) for field in arrow_schema],
        )

        # Get statistics
        relation_statistics = RelationStatistics()

        column_names = {col.field_id: col.name for col in iceberg_schema.columns}
        column_types = {col.field_id: col.field_type for col in iceberg_schema.columns}

        files = self.table.inspect.files()
        relation_statistics.record_count = pyarrow.compute.sum(files.column("record_count")).as_py()

        if "distinct_counts" in files.columns:
            for file in files.column("distinct_counts"):
                for k, v in file:
                    relation_statistics.set_cardinality_estimate(column_names[k], v)

        if "value_counts" in files.columns:
            for file in files.column("value_counts"):
                for k, v in file:
                    relation_statistics.add_count(column_names[k], v)

        for file in files.column("lower_bounds"):
            for k, v in file:
                relation_statistics.update_lower(
                    column_names[k], IcebergConnector.decode_iceberg_value(v, column_types[k])
                )

        for file in files.column("upper_bounds"):
            for k, v in file:
                relation_statistics.update_upper(
                    column_names[k], IcebergConnector.decode_iceberg_value(v, column_types[k])
                )

        self.relation_statistics = relation_statistics

        return self.schema

    def read_dataset(self, columns: list = None, **kwargs) -> pyarrow.Table:
        rows_read = 0
        limit = kwargs.get("limit")

        if columns is None:
            column_names = self.schema.column_names
        else:
            column_names = [col.source_column for col in columns]

        reader = self.table.scan(
            selected_fields=column_names,
        ).to_arrow_batch_reader()

        for batch in reader:
            if limit and rows_read + batch.num_rows > limit:
                batch = batch.slice(0, limit - rows_read)
            yield pyarrow.Table.from_batches([batch])
            rows_read += batch.num_rows
            if limit and rows_read >= limit:
                break

    @staticmethod
    def decode_iceberg_value(
        value: Union[int, float, bytes], data_type: str, scale: int = None
    ) -> Union[int, float, str, datetime, Decimal, bool]:
        """
        Decode Iceberg-encoded values based on the specified data type.

        Parameters:
            value: Union[int, float, bytes]
                The encoded value from Iceberg.
            data_type: str
                The type of the value ('int', 'long', 'float', 'double', 'timestamp', 'date', 'string', 'decimal', 'boolean').
            scale: int, optional
                Scale used for decoding decimal types, defaults to None.

        Returns:
            The decoded value in its original form.
        """
        import pyiceberg

        data_type_class = data_type.__class__

        if data_type_class in (pyiceberg.types.LongType,):
            return int.from_bytes(value, "little", signed=True)
        elif data_type_class in (pyiceberg.types.DoubleType,):
            # IEEE 754 encoded floats are typically decoded directly
            return struct.unpack("<d", value)[0]  # 8-byte IEEE 754 double
        elif data_type == "timestamp":
            # Iceberg stores timestamps as microseconds since epoch
            return datetime.fromtimestamp(value / 1_000_000)
        elif data_type == "date":
            # Iceberg stores dates as days since epoch (1970-01-01)
            return datetime(1970, 1, 1) + timedelta(days=value)
        elif data_type_class == pyiceberg.types.StringType:
            # Assuming UTF-8 encoded bytes (or already decoded string)
            return value.decode("utf-8") if isinstance(value, bytes) else str(value)
        elif str(data_type).startswith("decimal"):
            # Iceberg stores decimals as unscaled integers
            int_value = int.from_bytes(value, byteorder="big", signed=True)
            return Decimal(int_value) / (10**data_type.scale)
        elif data_type_class == pyiceberg.types.BooleanType:
            return bool(value)
        else:
            raise ValueError(f"Unsupported data type: {data_type}, {str(data_type)}")
