from abc import ABC, abstractmethod
from datetime import date
from datetime import datetime
from functools import cmp_to_key
from logging import getLogger
from pathlib import Path
from typing import List, Tuple, Union

import classifications as classif
import country_converter as coco
from currency_converter import CurrencyConverter, ECB_URL
import pandas as pd
from pint import DimensionalityError, UndefinedUnitError, UnitRegistry
import semantic_version

from dataio._classifications_helper import (
    filter_classifications,
    generate_classification_mapping,
    generate_classification_mapping_multi_column,
    increment_version,
)
from dataio.load import load
from dataio.save import save
from dataio.schemas import bonsai_api
from dataio.schemas.bonsai_api import *
from dataio.schemas.bonsai_api import DataResource

logger = getLogger("root")


class ResourceRepository(ABC):
    @abstractmethod
    def add_or_update_resource_list(self, resource: DataResource):
        raise NotImplementedError

    @abstractmethod
    def add_to_resource_list(self, resource: DataResource):
        raise NotImplementedError

    @abstractmethod
    def update_resource_list(self, resource: DataResource):
        raise NotImplementedError

    @abstractmethod
    def get_resource_info(self, **filters) -> DataResource | List[DataResource]:
        raise NotImplementedError

    @abstractmethod
    def resource_exists(self, resource: DataResource) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_dataframe_for_task(self) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def get_dataframe_for_resource(self, resource: DataResource) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def write_dataframe_for_resource(
        self, data: pd.DataFrame, resource: DataResource, overwrite=True
    ):
        raise NotImplementedError

    @abstractmethod
    def list_available_resources(self) -> list[DataResource]:
        raise NotImplementedError

    @abstractmethod
    def load_with_classification(
        self, classifications, **kwargs
    ) -> Tuple[pd.DataFrame, dict[str, set[str]]]:
        raise NotImplementedError

    @abstractmethod
    def load_with_bonsai_classification(
        self,
    ) -> Tuple[pd.DataFrame, dict[str, set[str]]]:
        raise NotImplementedError

    @abstractmethod
    def harmonize_with_resource(self, dataframe, **kwargs):
        raise NotImplementedError


class CSVResourceRepository(ResourceRepository):
    """
    Repository for managing data resources within a CSV file storage system.

    Attributes
    ----------
    db_path : Path
        Path to the directory containing the resource CSV file.
    table_name : str
        Name of the table (used for naming the CSV file).
    resources_list_path : Path
        Full path to the CSV file that stores resource information.
    schema : DataResource
        Schema used for resource data validation and storage.

    Methods
    -------
    add_or_update_resource_list(resource: DataResource, **kwargs)
        Adds a new resource or updates an existing one in the repository.
    add_to_resource_list(resource: DataResource)
        Adds a new resource to the repository.
    update_resource_list(resource: DataResource)
        Updates an existing resource in the repository.
    get_resource_info(**filters)
        Retrieves resource information based on specified filters.
    add_from_dataframe(data, loc, task_name, task_relation, last_update, **kwargs)
        Adds resource information from a DataFrame.
    get_dataframe_for_task(name, **kwargs)
        Retrieves a DataFrame for a specific task.
    write_dataframe_for_task(data, resource_name, **kwargs)
        Writes a DataFrame to the storage based on resource information.
    write_dataframe_for_resource(data, resource, overwrite)
        Validates and writes a DataFrame to the resource location.
    list_available_resources()
        Lists all available resources in the repository.
    comment_resource(resource, comment)
        Adds a comment to a resource and updates the repository.
    """

    def __init__(self, db_path: str, table_name="resources") -> None:
        """
        Initializes the ResourceRepository with the path to the database and table name.

        Parameters
        ----------
        db_path : str
            The file system path where the CSV database is located.
        table_name : str, optional
            The name of the table, default is 'resources'.
        """
        self.db_path = Path(db_path)
        self.table_name = table_name

        self.ureg = UnitRegistry()
        self.cc = coco.CountryConverter()
        self.currency_converter = CurrencyConverter(
            ECB_URL, fallback_on_missing_rate=True
        )

        if self.db_path.is_dir():
            self.resources_list_path = self.db_path / (self.table_name + ".csv")
        else:
            self.resources_list_path = self.db_path
        self.schema = DataResource

        csv_resource = DataResource(
            table_name, DataResource.__name__, location=str(self.resources_list_path)
        )
        self.resources_list_path = Path(csv_resource.location)
        self.root_dir = self.resources_list_path.parent.absolute()
        # Initialize CSV file if it does not exist
        if not self.resources_list_path.exists():
            if not self.resources_list_path.parent.exists():
                self.resources_list_path.parent.mkdir(parents=True)
            self.schema.get_empty_dataframe().to_csv(
                self.resources_list_path, index=False
            )

        self.available_resources = load(
            self.resources_list_path, {self.table_name: self.schema}
        )

        # If freshly initialized, set to empty pd.DataFrame
        # --> will be empty dict if this is the case
        if isinstance(self.available_resources, dict):
            self.available_resources = self.schema.get_empty_dataframe()

    def add_or_update_resource_list(self, resource: DataResource, **kwargs) -> None:
        """
        Adds a new resource to the repository or updates it if it already exists.

        Parameters
        ----------
        resource : DataResource
            The resource data to add or update.
        kwargs : dict
            Additional keyword arguments used for extended functionality.
        """

        if self.resource_exists(resource):
            self.update_resource_list(resource)
        else:
            self.add_to_resource_list(resource)

    def add_to_resource_list(self, resource: DataResource) -> None:
        """
        Appends a new resource to the repository.

        Parameters
        ----------
        resource : DataResource
            The resource data to add.
        """
        # Append new record
        new_record = resource.to_pandas()
        self.available_resources = pd.concat(
            [self.available_resources, new_record], ignore_index=True
        )
        self.available_resources.to_csv(self.resources_list_path, index=False)

    def update_resource_list(self, resource: DataResource) -> None:
        """
        Updates an existing resource in the repository.

        Parameters
        ----------
        resource : DataResource
            The resource data to update.
        """
        # Update existing record
        resource_as_dict = resource.to_pandas().squeeze().to_dict()
        cleared_dict = self._clear_resource_dict(resource_as_dict)
        mask = pd.Series([True] * len(self.available_resources))
        for key, value in cleared_dict.items():
            if not value:
                # None values will match with any available resource
                continue
            mask &= self.available_resources[key] == value

        row_index = self.available_resources[mask].index[0]

        for key, value in resource_as_dict.items():
            self.available_resources.at[row_index, key] = value

        self.available_resources.to_csv(self.resources_list_path, index=False)

    def _clear_resource_dict(self, resource_dict: dict):
        resource_dict = resource_dict.copy()
        # drop unnecessary fields
        if "comment" in resource_dict:
            del resource_dict["comment"]
        if "created_by" in resource_dict:
            del resource_dict["created_by"]
        if "license" in resource_dict:
            del resource_dict["license"]
        if "last_update" in resource_dict:
            del resource_dict["last_update"]
        if "license_url" in resource_dict:
            del resource_dict["license_url"]
        if "dag_run_id" in resource_dict:
            del resource_dict["dag_run_id"]

        return resource_dict

    def resource_exists(self, resource: DataResource) -> bool:
        try:
            model_dict = resource.to_pandas().squeeze().to_dict()
            model_dict = self._clear_resource_dict(model_dict)
            self.get_resource_info(**model_dict)
            return True
        except ValueError:
            return False

    def get_latest_version(self, **filters: dict):
        resources = self.get_resource_info(**filters)

        if not isinstance(resources, list):
            return resources

        if len(resources) > 1:

            def compare_version_strings(
                resource1: DataResource, resource2: DataResource
            ):
                try:
                    version1 = semantic_version.Version.coerce(resource1.data_version)
                    version2 = semantic_version.Version.coerce(resource2.data_version)
                    return (version1 > version2) - (version1 < version2)
                except ValueError:
                    # Fallback to regular string comparison if semantic_version fails
                    return (resource1.data_version > resource2.data_version) - (
                        resource1.data_version < resource2.data_version
                    )

            resources = sorted(
                resources, key=cmp_to_key(compare_version_strings), reverse=True
            )

        return resources[0]

    def get_resource_info(self, **filters: dict) -> DataResource | List[DataResource]:
        """
        Retrieves resource information based on specified filters.

        Parameters
        ----------
        filters : dict
            Key-value pairs of attributes to filter the resources by.

        Returns
        -------
        DataResource
            The matched resource data.
        List[DataResource]
            If more than one resource match the filters, a list with all of them is returned

        Raises
        ------
        ValueError
            If no resource is found or if multiple resources are found.
        """
        mask = pd.Series(True, index=self.available_resources.index)

        for k, v in filters.items():
            if not v:
                # None values will match with any available resource
                continue
            # Update the mask to narrow down the rows
            mask = mask & (self.available_resources[k] == v)
        result = self.available_resources[mask]

        if result.empty:
            raise ValueError(f"No resource found with the provided filters: {filters}")

        if len(result.index) > 1:
            results = []
            for _, row in result.iterrows():
                results.append(self._row_to_data_resource(row))
            return results
        else:
            return self._row_to_data_resource(result.iloc[0])

    def add_from_dataframe(
        self,
        data: pd.DataFrame,
        loc: Union[Path, str],
        task_name: str | None = None,
        task_relation: str = "output",
        last_update: date = date.today(),
        **kwargs,
    ) -> DataResource:
        res = DataResource.from_dataframe(
            data,
            loc,
            task_name,
            task_relation=task_relation,
            last_update=last_update,
            **kwargs,
        )
        self.add_or_update_to_list(res)
        return res

    def get_dataframe_for_task(
        self,
        name: str,
        **kwargs,
    ) -> pd.DataFrame:
        res = self.get_resource_info(
            name=name,
            **kwargs,
        )
        assert not isinstance(
            res, list
        ), "Provided information points to more than one resource. Please add more information."
        return load(
            Path(res.location), {Path(res.location).stem: globals()[res.schema_name]}
        )

    def get_dataframe_for_resource(self, res: DataResource):
        return load(
            Path(res.location), {Path(res.location).stem: globals()[res.schema_name]}
        )

    def write_dataframe_for_task(
        self,
        data: pd.DataFrame,
        resource_name: str,
        data_version: str,
        overwrite=True,
        **kwargs,
    ):
        try:
            # make sure only relevant fields are used when getting already existing resource
            cleaned_kwargs = self._clear_resource_dict(kwargs)
            resource = self.get_resource_info(name=resource_name, **cleaned_kwargs)

            if isinstance(resource, list):
                raise IndexError(
                    "Resource information is ambiguous. Multiple resources match the given description. Please provide more parameters."
                )
            # update resource based on kwargs
            for key, value in kwargs.items():
                if key == "location":
                    resource.__setattr__("_location", value)
                else:
                    resource.__setattr__(key, value)
        except ValueError:
            resource = DataResource(
                name=resource_name,
                data_version=data_version,
                root_location=self.root_dir,
                **kwargs,
            )

        resource.data_version = data_version
        self.write_dataframe_for_resource(data, resource, overwrite=overwrite)

    def write_dataframe_for_resource(
        self, data: pd.DataFrame, resource: DataResource, overwrite=True
    ):
        schema = globals()[resource.schema_name]

        if self.resource_exists(resource) and not overwrite:
            raise FileExistsError

        save(data, resource.name, Path(resource.location), schema, overwrite)
        self.add_or_update_resource_list(resource)

    def list_available_resources(self) -> list[DataResource]:
        resources = [
            self._row_to_data_resource(row)
            for _, row in self.available_resources.iterrows()
        ]
        return resources

    def comment_resource(self, resource: DataResource, comment: str) -> DataResource:
        resource.append_comment(comment)
        self.add_or_update_resource_list(resource)
        return resource

    def _row_to_data_resource(self, row):
        args = {"root_location": self.root_dir, **row}
        return DataResource(**args)

    def valid_units(self):
        return set(self.ureg) | self.currency_converter.currencies

    def _get_currency_unit_and_year(self, unit: str) -> tuple[str, object]:
        # Extract base currency and year if unit specifies a historical year
        if unit[-4:].isdigit():
            base_currency = unit[:-4].upper()
            year = datetime.datetime(int(unit[-4:]), 1, 1)
        else:
            base_currency = unit.upper()
            year = None
        return base_currency, year

    def convert_units(
        self, data: pd.DataFrame, target_units: list[str]
    ) -> pd.DataFrame:
        """
        Converts values in the 'value' column of a DataFrame to the specified target units in the list.
        Units not listed in the target_units remain unchanged.

        Args:
            dataframe (pd.DataFrame): A DataFrame with 'unit' and 'value' columns.
            target_units (list): A list of target units to convert compatible units to.
                                 Example: ["kg", "J", "m"]

        Returns:
            pd.DataFrame: A DataFrame with the converted values and target units.
        """

        # Check if input DataFrame has required columns
        if "unit" not in data.columns or "value" not in data.columns:
            raise ValueError("The DataFrame must contain 'unit' and 'value' columns.")

        # Check for the 'year' column
        use_historical = "year" in data.columns

        # Create columns for converted values and units
        new_values = []
        new_units = []

        no_target_units = set()
        not_defined_units = set()

        sanitized_targets = []
        for target in target_units:
            if target in self.ureg:
                sanitized_targets.append(target)
            else:
                potential_currency, _ = self._get_currency_unit_and_year(target)

                if potential_currency in self.currency_converter.currencies:
                    sanitized_targets.append(target)
                else:
                    logger.warning(
                        f"Target unit {target} not defined, will be skipped when converting"
                    )

        for _, row in data.iterrows():
            # Parse the current value and unit
            current_value = row["value"]
            current_unit = row["unit"]

            if not current_unit in self.ureg:
                # potentially a currency!
                potential_currency, _ = self._get_currency_unit_and_year(current_unit)
                if not potential_currency in self.currency_converter.currencies:
                    not_defined_units.add(current_unit)
                    new_values.append(current_value)
                    new_units.append(current_unit)
                    continue

            # Initialize target unit as None
            target_unit = None
            target_currency = None

            # Find a matching target unit based on dimensionality
            for target in sanitized_targets:
                try:
                    if (
                        self.ureg.parse_units(current_unit).dimensionality
                        == self.ureg.parse_units(target).dimensionality
                    ):
                        target_unit = target
                        break
                except UndefinedUnitError:
                    # Handle currency conversion
                    base_currency, base_year = self._get_currency_unit_and_year(
                        current_unit
                    )
                    new_currency, new_year = self._get_currency_unit_and_year(target)

                    if (
                        base_currency in self.currency_converter.currencies
                        and new_currency in self.currency_converter.currencies
                    ):
                        target_currency = new_currency
                        break

            if target_unit:
                # Convert the value
                quantity = self.ureg.Quantity(current_value, current_unit)
                converted_quantity = quantity.to(target_unit)
                new_values.append(converted_quantity.magnitude)
                new_units.append(target_unit)
            elif target_currency:

                # Get the historical date from the 'year' column
                historical_date = None
                if use_historical:
                    year = row["year"]
                    historical_date = (
                        datetime.datetime(int(year), 1, 1)
                        if not pd.isnull(year)
                        else None
                    )

                # If a year is defined in the target or in base unit use that over year column
                target_date = new_year or base_year or historical_date
                # Use the historical date if available
                if new_year and base_year and new_year != base_year:
                    logger.warning(
                        f"Both base year and target year are defined for currency conversion. Converting between different years is currently not supported. The currency is converted, assuming the base year {new_year} for both values."
                    )

                if target_date:
                    converted_value = self.currency_converter.convert(
                        current_value, base_currency, target_currency, date=target_date
                    )
                else:
                    converted_value = self.currency_converter.convert(
                        current_value, base_currency, target_currency
                    )

                new_values.append(converted_value)
                new_units.append(target_currency)
            else:
                no_target_units.add(current_unit)
                new_values.append(current_value)
                new_units.append(current_unit)

        if not_defined_units:
            logger.warning(
                f"The following units could not be converted because they are not defined in the unit registry: {not_defined_units}"
            )

        if no_target_units:
            logger.warning(
                f"The following units could not be converted because for their dimensionality no target unit was defined: {no_target_units}"
            )

        data["unit"] = new_units
        data["value"] = new_values

        return data

    def convert_dataframe_to_bonsai_classification(
        self, data: pd.DataFrame, original_schema
    ) -> Tuple[pd.DataFrame, dict[str, set[str]]]:
        return self.convert_dataframe(
            data,
            original_schema,
            classifications=classif.core.get_bonsai_classification(),
        )

    def convert_dataframe(
        self,
        data: pd.DataFrame,
        original_schema,
        classifications: dict,
        units: list[str] | None = None,
    ) -> Tuple[pd.DataFrame, dict[str, set[str]]]:
        unmapped_values: dict[str, set[str]] = dict()

        # Check if the class exists and has the method you want to call
        if original_schema and hasattr(original_schema, "get_classification"):
            from_class = original_schema.get_classification()
        else:
            raise AttributeError(
                f"{original_schema} does not have a 'get_classification' method."
            )

        concordances = {}
        pair_wise_concs = {}
        classif_to_columns_name = {}

        for column_name, (classif_name, classif_type) in from_class.items():
            if not classif_type in classifications:
                logger.warning(
                    f"No target classification provided for column name {column_name} [{classif_type}]"
                )
                continue
            classif_to_columns_name[classif_type] = column_name

            concordance = classif.get_concordance(
                classif_name, classifications[classif_type]
            )
            # this is a pairwise concordance and needs to be treated specificly
            if isinstance(concordance, pd.DataFrame) and len(concordance.columns) == 9:
                from_pair: list[str] = []
                to_pair: list[str] = []
                this_classif_columns = []
                for name in concordance.columns:
                    if "_from" in name and not name.startswith("classification"):
                        from_pair.append(name)
                    elif "_to" in name and not name.startswith("classification"):
                        to_pair.append(name)
                    if classif_type in name:
                        this_classif_columns.append(name)

                if tuple((tuple(from_pair), tuple(to_pair))) not in pair_wise_concs:
                    pair_wise_concs[tuple((tuple(from_pair), tuple(to_pair)))] = (
                        concordance
                    )

            else:
                concordances[column_name] = concordance

        missing = set(data.columns) - set(concordances)
        if any(missing):
            logger.info(f"No concordance found for columns: {missing}.")

        for (from_columns, to_columns), concordance in pair_wise_concs.items():
            # Select all columns that start with 'tree_'
            tree_columns = list(from_columns + to_columns)

            # Filter rows where none of the selected columns have NaNs
            dropped_rows = concordance[concordance[tree_columns].isna().any(axis=1)]
            filtered_concordance = concordance.dropna(subset=tree_columns)

            column_names = [
                classif_to_columns_name[c.split("_")[0]] for c in from_columns
            ]
            classif_names = [c.split("_")[0] for c in from_columns]

            # save the left_over concordances for indidual mapping afterwards
            for column_name, from_column, to_column in zip(
                column_names, from_columns, to_columns
            ):
                concordances[column_name] = (
                    dropped_rows[
                        [from_column, to_column]
                        + ["comment", "prefixed_id", "skos_uri"]
                    ]
                    .copy()
                    .dropna()
                )

            mapping_dict, to_be_summed = generate_classification_mapping_multi_column(
                filtered_concordance, classif_names
            )

            # Step 2: Define a function to map activitytype and flowobject together
            def map_to_bonsai(row, column_names, mapping_dict):
                key = (row[column_names[0]], row[column_names[1]])
                if (
                    pd.notna(row[column_names[0]])
                    and pd.notna(row[column_names[1]])
                    and key in mapping_dict
                ):
                    return mapping_dict[key]  # Return the mapped bonsai values
                else:
                    return (
                        row[column_names[0]],
                        row[column_names[1]],
                    )  # Keep original values if no mapping exists

            # Step 3: Apply the mapping function to the DataFrame
            data[column_names] = data.apply(
                lambda row: pd.Series(map_to_bonsai(row, column_names, mapping_dict)),
                axis=1,
            )

        for column, concordance in concordances.items():
            if column not in data.columns:
                logger.info(
                    f"Skipping concordance {column} as there are no corresponding columns found for it"
                )
                continue  # Skip if the column doesn't exist in the dataframe

            unmapped_values[column] = set()

            # Handle specific case for 'location' column
            if from_class[column][1] == "location":

                def convert_location_with_unmapped(value, to, src=None):
                    if src:
                        converted_value = coco.convert(names=value, src=src, to=to)
                    else:
                        converted_value = coco.convert(names=value, to=to)
                    if converted_value == "not found":  # Check for "not found" case
                        unmapped_values[column].add(value)
                        return value  # Keep the original value
                    return converted_value

                if from_class[column][0] in self.cc.valid_class:
                    data[column] = data[column].apply(
                        lambda x: convert_location_with_unmapped(
                            x, to=classifications[column], src=from_class[column][0]
                        )
                    )
                else:
                    logger.warning(
                        f"{from_class[column][0]} not a valid coco classification, trying anyway..."
                    )
                    data[column] = data[column].apply(
                        lambda x: convert_location_with_unmapped(
                            x, to=classifications[column]
                        )
                    )
            else:
                # filter many to many correspondences since they can't be used
                # use the valid correspondences only
                filtered_correspondence = filter_classifications(concordance)

                # Generate and apply classification mapping
                mapping_dict, codes_to_be_summed = generate_classification_mapping(
                    filtered_correspondence, from_class[column][1]
                )

                # Apply transformation with a lambda function that tracks unmapped values
                data[column] = data[column].apply(
                    lambda x: (
                        mapping_dict[x]
                        if x in mapping_dict
                        else unmapped_values[column].add(x) or x
                    )
                )

                if codes_to_be_summed:
                    # Grouping function to handle unit compatibility
                    def group_and_sum(df, code_column, group_columns, values_to_sum):
                        results = []
                        for value in values_to_sum:
                            group = df[df[code_column] == value].copy()
                            if not group.empty:
                                # Further group by all columns except 'Value' and 'Unit'
                                grouped = group.groupby(group_columns, as_index=False)
                                for _, sub_group in grouped:
                                    try:
                                        # Attempt to convert all values to the first unit in the subgroup
                                        base_unit = sub_group["unit"].iloc[0]
                                        sub_group["base_value"] = sub_group.apply(
                                            lambda row: (
                                                row["value"] * self.ureg(row["unit"])
                                            )
                                            .to(base_unit)
                                            .magnitude,
                                            axis=1,
                                        )
                                        # Sum the converted values
                                        summed_value = sub_group["base_value"].sum()
                                        sub_group.drop(
                                            columns=["base_value"], inplace=True
                                        )
                                        result = sub_group.iloc[0].copy()
                                        result["value"] = summed_value
                                        result["unit"] = base_unit
                                        results.append(result.to_dict())
                                    except DimensionalityError:
                                        # If units are not compatible, append the rows as is
                                        results.extend(sub_group.to_dict("records"))
                                    except UndefinedUnitError:
                                        # If units are not found in pint, append the rows as is
                                        results.extend(sub_group.to_dict("records"))
                        return pd.DataFrame(results)

                    # Group by all columns except 'Value' and 'Unit'
                    ignore_columns = ["value", "unit"]
                    group_columns = [
                        col for col in data.columns if col not in ignore_columns
                    ]

                    # Apply the grouping and summing function
                    summed_df = group_and_sum(
                        data, column, group_columns, codes_to_be_summed
                    )

                    # Keep rows not in values_to_sum
                    remaining_df = data[~data[column].isin(list(codes_to_be_summed))]

                    # Combine the summed and remaining DataFrames
                    data = pd.concat([summed_df, remaining_df], ignore_index=True)

            if unmapped_values[column]:
                logger.info(
                    f"Unmapped classifications in column {column}: {unmapped_values[column]}"
                )

        if units:
            data = self.convert_units(data, units)

        return data, unmapped_values

    def load_with_classification(
            self, classifications: dict, units: (list[str]|None) = None, **kwargs
    ) -> Tuple[pd.DataFrame, dict[str, set[str]]]:
        """
        loads data with a certain classificaiton. for the selected fields. Rows that can't
        be automatically transformed are ignored and returned as is
        """
        # Retrieve resource information and dataframe for task
        resource_info = self.get_resource_info(**kwargs)
        data = self.get_dataframe_for_task(**kwargs)

        schema_name = resource_info.schema_name
        schema_class = getattr(bonsai_api, schema_name, None)

        return self.convert_dataframe(
            data, original_schema=schema_class, classifications=classifications, units=units
        )

    def load_with_bonsai_classification(
        self, **kwargs
    ) -> Tuple[pd.DataFrame, dict[str, set[str]]]:
        """
        This method loads the selected data based on kwargs with the default BONSAI classifications.
        The default classifications for BONSAI are the following:

        location: ISO3
        flowobject: BONSAI
        """

        return self.load_with_classification(
            classifications=classif.core.get_bonsai_classification(), **kwargs
        )

    def harmonize_with_resource(self, dataframe, **kwargs):
        # Load the base DataFrame
        base_df = self.get_dataframe_for_task(**kwargs)

        # Define the columns to check for overlaps
        overlap_columns = ["time", "location", "product", "unit"]

        # Ensure the overlap columns exist in both DataFrames
        for column in overlap_columns:
            if column not in base_df.columns or column not in dataframe.columns:
                raise ValueError(
                    f"Column '{column}' is missing in one of the DataFrames"
                )

        # Concatenate the DataFrames
        combined_df = pd.concat([base_df, dataframe], ignore_index=True)

        # Identify duplicate rows based on overlap columns
        duplicates = combined_df[
            combined_df.duplicated(subset=overlap_columns, keep=False)
        ]
        # TODO handle dublicates somehow. Based on source and uncertainty

        # Find and display duplicate pairs
        duplicate_pairs = (
            combined_df.groupby(overlap_columns).size().reset_index(name="Count")
        )
        duplicate_pairs = duplicate_pairs[duplicate_pairs["Count"] > 1]

        # # Display all duplicate pairs
        # if not duplicate_pairs.empty:
        #     print("Duplicate Pairs:")
        #     print(duplicate_pairs)
        # else:
        #     print("No duplicate pairs found.")

        duplicates_df = duplicates
        unique_df = combined_df.drop_duplicates(subset=overlap_columns, keep=False)
        # TODO check if there is any changes if not then no need to create a new resource

        resource = self.get_latest_version(**kwargs)
        resource.data_version = increment_version(resource.data_version)
        self.write_dataframe_for_resource(unique_df, resource)
