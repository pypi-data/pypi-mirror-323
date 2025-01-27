import logging
from copy import copy
from typing import List, Tuple

import pyspark.sql.functions as F
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, lit
from sws_api_client import Tags
from sws_api_client.tags import BaseDisseminatedTagTable, TableLayer, TableType

from .constants import IcebergDatabases, IcebergTables
from .SWSPostgresSparkReader import SWSPostgresSparkReader
from .utils import (
    col_is_null_or_empty,
    get_or_create_tag,
    save_cache_csv,
    upsert_disseminated_table,
)


class SWSGoldIcebergSparkHelper:
    def __init__(
        self,
        spark: SparkSession,
        bucket: str,
        tag_name: str,
        dataset_id: str,
        sws_postgres_spark_reader: SWSPostgresSparkReader,
        iceberg_tables: IcebergTables,
        domain_code: str,
        dataset_details: dict = None,
    ) -> None:
        self.spark: SparkSession = spark
        self.dataset_details: dict = dataset_details
        self.bucket: str = bucket
        self.tag_name: str = tag_name
        self.dataset_id: str = dataset_id
        self.sws_postgres_spark_reader = sws_postgres_spark_reader
        self.iceberg_tables: IcebergTables = iceberg_tables
        self.domain_code = domain_code

        if dataset_details is not None:
            (
                self.dim_columns_w_time,
                self.dim_columns,
                self.time_column,
                self.flag_columns,
            ) = self._get_dim_time_flag_columns()

            self.cols_to_keep_sdmx = (
                self.dim_columns_w_time
                + ["unit_of_measure", "unit_of_measure_multiplier", "value"]
                + self.flag_columns
            )
            self.cols_to_keep_sws = (
                self.dim_columns_w_time + ["value"] + self.flag_columns
            )

            # ----------------
            # Get the codelist -> type mapping (e.g. geographicAreaM49 -> area )
            # ----------------
            self.codelist_type_mapping = (
                self.sws_postgres_spark_reader.get_codelist_type_mapping(
                    self.domain_code,
                    dimension_flag_columns=self.dim_columns_w_time + self.flag_columns,
                )
            )

            self.mapping_dim_col_name_type = {
                col_name: col_type
                for col_name, col_type in self.codelist_type_mapping.items()
                if col_name in self.dim_columns
            }

            (
                self.df_mapping_sdmx_codes,
                self.df_mapping_sdmx_uom,
                self.df_mapping_sdmx_col_names,
            ) = sws_postgres_spark_reader.import_sdmx_mapping_datatables(self.domain_code)

            self._check_column_mappings(self.df_mapping_sdmx_col_names)

    def _check_column_mappings(
        self,
        df_mapping_sdmx_col_names: DataFrame,
    ) -> DataFrame:
        cols_to_keep_set = set(self.cols_to_keep_sdmx)
        mapping_sdmx_col_names_internal_set = {
            row[0]
            for row in df_mapping_sdmx_col_names.filter(
                col("internal_name").isNotNull() & (col("internal_name") != lit(""))
            )
            .select("internal_name")
            .collect()
        }

        if not (cols_to_keep_set <= mapping_sdmx_col_names_internal_set):
            missing_mappings = cols_to_keep_set - mapping_sdmx_col_names_internal_set

            message = 'The mappings in the table "Mapping - SDMX columns names" are not correct'

            if len(missing_mappings) > 0:
                message += (
                    f"\nThe following column mappings are missing: {missing_mappings}"
                )

            raise ValueError(message)

    def _get_dim_time_flag_columns(self) -> Tuple[List[str], List[str], str, List[str]]:
        """Extract the dimension columns with time, without time, the time column and the flag columns names."""
        dim_columns_w_time = [
            dimension["id"] for dimension in self.dataset_details.get("dimensions", [])
        ]
        time_column = next(
            dimension["id"]
            for dimension in self.dataset_details.get("dimensions", [])
            if dimension["codelist"]["type"] == "time"
        )
        dim_columns = copy(dim_columns_w_time)
        dim_columns.remove(time_column)

        flag_columns = [flag["id"] for flag in self.dataset_details.get("flags", [])]

        return dim_columns_w_time, dim_columns, time_column, flag_columns

    def apply_diss_flag_filter(self, df: DataFrame) -> DataFrame:
        return df.filter(col("diss_flag"))

    # TODO implement the delete flag
    def apply_uom_mapping(
        self,
        df: DataFrame,
    ) -> DataFrame:
        logging.info("mapping unit of measure for dissemination")

        df = df.withColumn(
            "official_sws_uom",
            F.when(
                col_is_null_or_empty("unit_of_measure_base_unit"),
                col("unit_of_measure"),
            ).otherwise(col("unit_of_measure_base_unit")),
        ).withColumn(
            "official_sws_multiplier",
            F.coalesce(F.log10(col("unit_of_measure_multiplier")), lit(0)).cast("int"),
        )

        delete_df_uom_mapping = self.df_mapping_sdmx_uom.filter(
            col("delete")
            & col_is_null_or_empty("sdmx_code")
            & col("sdmx_multiplier").isNull()
            & col("value_multiplier").isNull()
        )

        generic_df_uom_mapping = self.df_mapping_sdmx_uom.filter(
            ~col("delete")
            & col("sws_multiplier").isNull()
            & col("sdmx_multiplier").isNull()
            & (col("value_multiplier") == lit(0))
        )

        specific_df_uom_mapping = self.df_mapping_sdmx_uom.filter(
            ~col("delete")
            & col("sws_multiplier").isNotNull()
            & col("sdmx_multiplier").isNotNull()
        )

        # Apply generic uom mapping
        df = (
            df.alias("d")
            .join(
                generic_df_uom_mapping.alias("m"),
                col("d.official_sws_uom") == col("m.sws_code"),
                "left",
            )
            .select("d.*", col("sdmx_code").alias("generic_sdmx_uom"))
        )

        # Apply specific uom mapping
        df = (
            df.alias("d")
            .join(
                specific_df_uom_mapping.alias("m"),
                (col("d.official_sws_uom") == col("m.sws_code"))
                & (col("d.official_sws_multiplier") == col("m.sws_multiplier")),
                "left",
            )
            .select(
                "d.*",
                col("sdmx_code").alias("specific_sdmx_uom"),
                col("sdmx_multiplier").alias("specific_sdmx_multiplier"),
                (col("value") * F.pow(lit(10), col("value_multiplier"))).alias(
                    "specific_sdmx_value"
                ),
            )
        )

        # Select the official values according to descending specificity
        df = (
            df.withColumn(
                "unit_of_measure",
                F.coalesce(
                    col("specific_sdmx_uom"),
                    col("generic_sdmx_uom"),
                    col("official_sws_uom"),
                ),
            )
            .withColumn(
                "unit_of_measure_multiplier",
                F.coalesce(
                    col("specific_sdmx_multiplier"), col("official_sws_multiplier")
                ),
            )
            .withColumn(
                "value",
                F.coalesce(col("specific_sdmx_value"), col("value")),
            )
            # Remove the columns that were not in the original dataset
            .drop(
                col("specific_sdmx_uom"),
                col("specific_sdmx_multiplier"),
                col("specific_sdmx_value"),
                col("generic_sdmx_uom"),
                col("official_sws_uom"),
                col("official_sws_multiplier"),
            )
        )

        return df

    def keep_dim_uom_val_attr_columns(self, df: DataFrame):
        return df.select(*self.cols_to_keep_sdmx)

    def keep_dim_val_attr_columns(self, df: DataFrame):
        return df.select(*self.cols_to_keep_sws)

    def _apply_sdmx_dimension_codes_mapping_single(
        self,
        df: DataFrame,
        dimension_name: str,
        dimension_type: str,
    ) -> DataFrame:
        logging.info(
            f"mapping column {dimension_name} of type {dimension_type} for dissemination"
        )
        return (
            df.alias("d")
            # Join the data with the standard mapping for the specific dimension
            .join(
                F.broadcast(
                    self.df_mapping_sdmx_codes.filter(
                        (col("domain").isNull() | (col("domain") == lit("")))
                        & (col("var_type") == lit(dimension_type))
                        & (
                            col("mapping_type").isNull()
                            | (col("mapping_type") == lit(""))
                        )
                    )
                ).alias("m_standard"),
                col(f"d.{dimension_name}") == col("m_standard.internal_code"),
                "left",
            )
            # Join the data with the domain specific mapping for the specific dimension
            .join(
                F.broadcast(
                    self.df_mapping_sdmx_codes.filter(
                        (col("domain") == lit(self.domain_code))
                        & (col("var_type") == lit(dimension_type))
                        & (
                            col("mapping_type").isNull()
                            | (col("mapping_type") == lit(""))
                        )
                    )
                ).alias("m_domain"),
                col(f"d.{dimension_name}") == col("m_domain.internal_code"),
                "left",
            )
            # Select only the columns we are interested in (this step is optional but recommended for debugging)
            .select(
                "d.*",
                col("m_standard.external_code").alias("standard_external_code"),
                col("m_standard.delete").alias("standard_delete"),
                col("m_standard.multiplier").alias("standard_multiplier"),
                col("m_domain.external_code").alias("domain_specific_external_code"),
                col("m_domain.delete").alias("domain_specific_delete"),
                col("m_domain.multiplier").alias("domain_specific_multiplier"),
            )
            # Filter out records to delete
            .filter(
                # Evaluate first the domain specific flag
                F.when(
                    col("domain_specific_delete").isNotNull(),
                    ~col("domain_specific_delete"),
                )
                # Then evaluate the general flag
                .when(
                    col("standard_delete").isNotNull(), ~col("standard_delete")
                ).otherwise(lit(True))
            )
            .withColumn(
                dimension_name,
                # Evaluate first the domain specific mapping
                F.when(
                    col("domain_specific_external_code").isNotNull(),
                    col("domain_specific_external_code"),
                )
                # Then evaluate the general mapping
                .when(
                    col("standard_external_code").isNotNull(),
                    col("standard_external_code"),
                ).otherwise(col(dimension_name)),
            )
            .withColumn(
                "value",
                # Multiply first by the domain specific multiplier
                F.when(
                    col("domain_specific_multiplier").isNotNull(),
                    col("value") * col("domain_specific_multiplier"),
                )
                # Then multiply by the general multiplier
                .when(
                    col("standard_external_code").isNotNull(),
                    col("value") * col("standard_multiplier"),
                ).otherwise(col("value")),
            )
            # Remove the columns that were not in the original dataset
            .drop(
                "standard_external_code",
                "standard_delete",
                "standard_multiplier",
                "domain_specific_external_code",
                "domain_specific_delete",
                "domain_specific_multiplier",
            )
        )

    def apply_sdmx_dimension_codes_mapping(self, df: DataFrame) -> DataFrame:
        logging.info("Mapping codes to comply with SDMX standard")
        for dimension_name, dimension_type in self.codelist_type_mapping.items():
            df = df.transform(
                self._apply_sdmx_dimension_codes_mapping_single,
                dimension_name=dimension_name,
                dimension_type=dimension_type,
            )

        return df

    def drop_non_sdmx_columns(self, df: DataFrame) -> DataFrame:
        cols_to_drop = [
            row["internal_name"]
            for row in self.df_mapping_sdmx_col_names.collect()
            if row["delete"] is True
        ]
        logging.info(f"Dropping non-SDMX columns: {cols_to_drop}")
        return df.drop(*cols_to_drop)

    def apply_sdmx_column_names_mapping(self, df: DataFrame) -> DataFrame:
        logging.info("Renaming columns to comply with SDMX standard")

        mapping_sws_col_sdmx_col = {
            row["internal_name"]: row["external_name"]
            for row in self.df_mapping_sdmx_col_names.filter(
                col("internal_name").isNotNull()
                & (col("internal_name") != lit(""))
                & ~col("delete")
            ).collect()
        }

        logging.info(f"Column names mappings: {mapping_sws_col_sdmx_col}")

        return df.withColumnsRenamed(mapping_sws_col_sdmx_col)

    def add_sdmx_default_columns(self, df: DataFrame) -> DataFrame:
        col_w_default_value = {
            row["external_name"]: row["default_value"]
            for row in self.df_mapping_sdmx_col_names.collect()
            if row["add"] is True
        }

        logging.info("Adding SDMX columns with default values")

        for name, default_value in col_w_default_value.items():
            logging.info(
                f"Adding SDMX column {name} with default value {default_value}"
            )
            df = df.withColumn(name, lit(default_value))

        return df

    def rearrange_sdmx_columns(self, df: DataFrame) -> DataFrame:
        logging.info(
            "Rearranging the columns to have the following order: Dimensions, TimeDimension, PrimaryMeasure, Attributes"
        )

        get_columns_for_type = lambda df, type: [
            row[0]
            for row in df.filter(col("type") == lit(type))
            .select("external_name")
            .collect()
        ]

        df_mapping_sdmx_no_del = self.df_mapping_sdmx_col_names.filter(~col("delete"))

        dimensions = get_columns_for_type(df_mapping_sdmx_no_del, "Dimension")
        time_dimensions = get_columns_for_type(df_mapping_sdmx_no_del, "TimeDimension")
        primary_measure = get_columns_for_type(df_mapping_sdmx_no_del, "PrimaryMeasure")
        attributes = get_columns_for_type(df_mapping_sdmx_no_del, "Attribute")

        logging.info(f"Dimensions: {dimensions}")
        logging.info(f"Time Dimensions: {time_dimensions}")
        logging.info(f"Primary Measure: {primary_measure}")
        logging.info(f"Attributes: {attributes}")

        return df.select(*dimensions, *time_dimensions, *primary_measure, *attributes)

    def gen_gold_sws_disseminated_data(self) -> DataFrame:
        return (
            self.spark.read.option("tag", self.tag_name)
            .table(self.iceberg_tables.SILVER.iceberg_id)
            .transform(self.apply_diss_flag_filter)
            .transform(self.keep_dim_val_attr_columns)
        )

    def gen_gold_sws_validated_data(self) -> DataFrame:
        return (
            self.spark.read.option("tag", self.tag_name)
            .table(self.iceberg_tables.BRONZE.iceberg_id)
            .transform(self.keep_dim_val_attr_columns)
        )

    def gen_gold_sdmx_data(self) -> DataFrame:
        return (
            self.spark.read.option("tag", self.tag_name)
            .table(self.iceberg_tables.SILVER.iceberg_id)
            .transform(self.apply_diss_flag_filter)
            .transform(self.apply_uom_mapping)
            .transform(self.keep_dim_uom_val_attr_columns)
            .transform(self.apply_sdmx_dimension_codes_mapping)
            .transform(self.apply_sdmx_column_names_mapping)
            .transform(self.add_sdmx_default_columns)
            .transform(self.rearrange_sdmx_columns)
        )

    def write_gold_sws_validated_data_to_iceberg_and_csv(
        self, df: DataFrame
    ) -> DataFrame:
        df.writeTo(self.iceberg_tables.GOLD_SWS_VALIDATED.iceberg_id).createOrReplace()

        logging.info(
            f"Gold SWS validated table written to {self.iceberg_tables.GOLD_SWS_VALIDATED.iceberg_id}"
        )

        self.spark.sql(
            f"ALTER TABLE {self.iceberg_tables.GOLD_SWS_VALIDATED.iceberg_id} CREATE OR REPLACE TAG `{self.tag_name}`"
        )

        logging.info(f"gold SWS validated tag '{self.tag_name}' created")

        df_1 = df.coalesce(1)

        save_cache_csv(
            df=df_1,
            bucket=self.bucket,
            prefix=self.iceberg_tables.GOLD_SWS_VALIDATED.csv_prefix,
            tag_name=self.tag_name,
        )

        return df

    def gen_and_write_gold_sws_validated_data_to_iceberg_and_csv(self) -> DataFrame:
        self.df_gold_sws_validated = self.gen_gold_sws_validated_data()

        self.write_gold_sws_validated_data_to_iceberg_and_csv(
            self.df_gold_sws_validated
        )

        return self.df_gold_sws_validated

    def write_gold_sws_disseminated_data_to_iceberg_and_csv(
        self, df: DataFrame
    ) -> DataFrame:
        df.writeTo(
            self.iceberg_tables.GOLD_SWS_DISSEMINATED.iceberg_id
        ).createOrReplace()

        logging.info(
            f"Gold SWS disseminated table written to {self.iceberg_tables.GOLD_SWS_DISSEMINATED.iceberg_id}"
        )

        self.spark.sql(
            f"ALTER TABLE {self.iceberg_tables.GOLD_SWS_DISSEMINATED.iceberg_id} CREATE OR REPLACE TAG `{self.tag_name}`"
        )

        logging.info(f"gold SWS disseminated tag '{self.tag_name}' created")

        df_1 = df.coalesce(1)

        save_cache_csv(
            df=df_1,
            bucket=self.bucket,
            prefix=self.iceberg_tables.GOLD_SWS_DISSEMINATED.csv_prefix,
            tag_name=self.tag_name,
        )

        return df

    def gen_and_write_gold_sws_disseminated_data_to_iceberg_and_csv(self) -> DataFrame:
        self.df_gold_sws_disseminated = self.gen_gold_sws_disseminated_data()

        self.write_gold_sws_disseminated_data_to_iceberg_and_csv(
            self.df_gold_sws_disseminated
        )

        return self.df_gold_sws_disseminated

    def write_gold_sdmx_data_to_iceberg_and_csv(self, df: DataFrame) -> DataFrame:
        df.writeTo(self.iceberg_tables.GOLD_SDMX.iceberg_id).createOrReplace()

        logging.info(
            f"Gold SDMX table written to {self.iceberg_tables.GOLD_SDMX.iceberg_id}"
        )

        self.spark.sql(
            f"ALTER TABLE {self.iceberg_tables.GOLD_SDMX.iceberg_id} CREATE OR REPLACE TAG `{self.tag_name}`"
        )

        logging.info(f"gold SDMX tag '{self.tag_name}' created")

        df_1 = df.coalesce(1)

        save_cache_csv(
            df=df_1,
            bucket=self.bucket,
            prefix=self.iceberg_tables.GOLD_SDMX.csv_prefix,
            tag_name=self.tag_name,
        )

        return df

    def gen_and_write_gold_sdmx_data_to_iceberg_and_csv(self) -> DataFrame:
        self.df_gold_sdmx = self.gen_gold_sdmx_data()

        self.write_gold_sdmx_data_to_iceberg_and_csv(self.df_gold_sdmx)

        return self.df_gold_sdmx

    def write_gold_sws_validated_sws_dissemination_tag(
        self, df: DataFrame, tags: Tags
    ) -> DataFrame:
        # Get or create a new tag
        tag = get_or_create_tag(tags, self.dataset_id, self.tag_name, self.tag_name)
        logging.debug(f"Tag: {tag}")

        new_iceberg_table = BaseDisseminatedTagTable(
            id=f"{self.domain_code.lower()}_gold_sws_validated_iceberg",
            name=f"{self.domain_code} gold SWS validated Iceberg",
            description="Gold table containing all the data unmapped and unfiltered in SWS compatible format",
            layer=TableLayer.GOLD,
            private=True,
            type=TableType.ICEBERG,
            database=IcebergDatabases.GOLD_DATABASE,
            table=self.iceberg_tables.GOLD_SWS_VALIDATED.table,
            path=self.iceberg_tables.GOLD_SWS_VALIDATED.path,
            structure={"columns": df.schema.jsonValue()["fields"]},
        )
        tag = upsert_disseminated_table(
            sws_tags=tags,
            tag=tag,
            dataset_id=self.dataset_id,
            tag_name=self.tag_name,
            table=new_iceberg_table,
        )
        logging.debug(f"Tag with Added Iceberg Table: {tag}")

        new_sdmx_table = BaseDisseminatedTagTable(
            id=f"{self.domain_code.lower()}_gold_sws_validated_csv",
            name=f"{self.domain_code} gold SWS validated csv",
            description="Gold table containing all the data unmapped and unfiltered in SWS compatible format cached in csv",
            layer=TableLayer.GOLD,
            private=True,
            type=TableType.CSV,
            path=self.iceberg_tables.GOLD_SWS_VALIDATED.csv_path,
            structure={"columns": df.schema.jsonValue()["fields"]},
        )
        tag = upsert_disseminated_table(
            sws_tags=tags,
            tag=tag,
            dataset_id=self.dataset_id,
            tag_name=self.tag_name,
            table=new_sdmx_table,
        )
        logging.debug(f"Tag with Added csv Table: {tag}")

        return df

    def write_gold_sws_disseminated_sws_dissemination_tag(
        self, df: DataFrame, tags: Tags
    ) -> DataFrame:
        # Get or create a new tag
        tag = get_or_create_tag(tags, self.dataset_id, self.tag_name, self.tag_name)
        logging.debug(f"Tag: {tag}")

        new_iceberg_table = BaseDisseminatedTagTable(
            id=f"{self.domain_code.lower()}_gold_sws_disseminated_iceberg",
            name=f"{self.domain_code} gold SWS disseminated Iceberg",
            description="Gold table containing all the data mapped and filtered in SWS compatible format",
            layer=TableLayer.GOLD,
            private=True,
            type=TableType.ICEBERG,
            database=IcebergDatabases.GOLD_DATABASE,
            table=self.iceberg_tables.GOLD_SWS_DISSEMINATED.table,
            path=self.iceberg_tables.GOLD_SWS_DISSEMINATED.path,
            structure={"columns": df.schema.jsonValue()["fields"]},
        )
        tag = upsert_disseminated_table(
            sws_tags=tags,
            tag=tag,
            dataset_id=self.dataset_id,
            tag_name=self.tag_name,
            table=new_iceberg_table,
        )
        logging.debug(f"Tag with Added Iceberg Table: {tag}")

        new_sdmx_table = BaseDisseminatedTagTable(
            id=f"{self.domain_code.lower()}_gold_sws_disseminated_csv",
            name=f"{self.domain_code} gold SWS disseminated csv",
            description="Gold table containing all the data mapped and filtered in SWS compatible format format cached in csv",
            layer=TableLayer.GOLD,
            private=True,
            type=TableType.CSV,
            path=self.iceberg_tables.GOLD_SWS_DISSEMINATED.csv_path,
            structure={"columns": df.schema.jsonValue()["fields"]},
        )
        tag = upsert_disseminated_table(
            sws_tags=tags,
            tag=tag,
            dataset_id=self.dataset_id,
            tag_name=self.tag_name,
            table=new_sdmx_table,
        )
        logging.debug(f"Tag with Added csv Table: {tag}")

        return df

    def write_gold_sdmx_sws_dissemination_tag(
        self, df: DataFrame, tags: Tags
    ) -> DataFrame:
        # Get or create a new tag
        tag = get_or_create_tag(tags, self.dataset_id, self.tag_name, self.tag_name)
        logging.debug(f"Tag: {tag}")

        new_iceberg_table = BaseDisseminatedTagTable(
            id=f"{self.domain_code.lower()}_gold_sdmx_iceberg",
            name=f"{self.domain_code} gold SDMX Iceberg",
            description="Gold table containing all the cleaned data in SDMX compatible format",
            layer=TableLayer.GOLD,
            private=True,
            type=TableType.ICEBERG,
            database=IcebergDatabases.GOLD_DATABASE,
            table=self.iceberg_tables.GOLD_SDMX.table,
            path=self.iceberg_tables.GOLD_SDMX.path,
            structure={"columns": df.schema.jsonValue()["fields"]},
        )
        tag = upsert_disseminated_table(
            sws_tags=tags,
            tag=tag,
            dataset_id=self.dataset_id,
            tag_name=self.tag_name,
            table=new_iceberg_table,
        )
        logging.debug(f"Tag with Added Iceberg Table: {tag}")

        new_sdmx_table = BaseDisseminatedTagTable(
            id=f"{self.domain_code.lower()}_gold_sdmx_csv",
            name=f"{self.domain_code} gold SDMX csv",
            description="Gold table containing all the cleaned data in SDMX compatible format cached in csv",
            layer=TableLayer.GOLD,
            private=True,
            type=TableType.CSV,
            path=self.iceberg_tables.GOLD_SDMX.csv_path,
            structure={"columns": df.schema.jsonValue()["fields"]},
        )
        tag = upsert_disseminated_table(
            sws_tags=tags,
            tag=tag,
            dataset_id=self.dataset_id,
            tag_name=self.tag_name,
            table=new_sdmx_table,
        )
        logging.debug(f"Tag with Added csv Table: {tag}")

        return df
