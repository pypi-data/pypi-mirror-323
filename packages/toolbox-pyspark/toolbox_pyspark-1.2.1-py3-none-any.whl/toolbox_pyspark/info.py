# ============================================================================ #
#                                                                              #
#     Title: Info                                                              #
#     Purpose: Provide utility functions for retrieving information from       #
#              `pyspark` dataframes.                                           #
#                                                                              #
# ============================================================================ #


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Overview                                                              ####
#                                                                              #
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
#  Description                                                              ####
# ---------------------------------------------------------------------------- #


"""
!!! note "Summary"
    The `info` module is used to provide utility functions for retrieving information from `pyspark` dataframes.
"""


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Setup                                                                 ####
#                                                                              #
# ---------------------------------------------------------------------------- #


## --------------------------------------------------------------------------- #
##  Imports                                                                 ####
## --------------------------------------------------------------------------- #


# ## Python StdLib Imports ----
from typing import Any, Optional, Union

# ## Python Third Party Imports ----
from numpy import ndarray as npArray
from pandas import DataFrame as pdDataFrame
from pyspark.sql import DataFrame as psDataFrame, types as T
from toolbox_python.checkers import is_type
from toolbox_python.collection_types import str_collection, str_list
from typeguard import typechecked

# ## Local First Party Imports ----
from toolbox_pyspark.checks import assert_column_exists
from toolbox_pyspark.constants import (
    LITERAL_LIST_OBJECT_NAMES,
    LITERAL_NUMPY_ARRAY_NAMES,
    LITERAL_PANDAS_DATAFRAME_NAMES,
    LITERAL_PYSPARK_DATAFRAME_NAMES,
    VALID_LIST_OBJECT_NAMES,
    VALID_NUMPY_ARRAY_NAMES,
    VALID_PANDAS_DATAFRAME_NAMES,
    VALID_PYSPARK_DATAFRAME_NAMES,
)


## --------------------------------------------------------------------------- #
##  Exports                                                                 ####
## --------------------------------------------------------------------------- #


__all__: str_list = ["get_distinct_values", "extract_column_values"]


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Main Section                                                          ####
#                                                                              #
# ---------------------------------------------------------------------------- #


## --------------------------------------------------------------------------- #
##  `get_*()` functions                                                     ####
## --------------------------------------------------------------------------- #


@typechecked
def extract_column_values(
    dataframe: psDataFrame,
    column: str,
    distinct: bool = True,
    return_type: Union[
        LITERAL_PYSPARK_DATAFRAME_NAMES,
        LITERAL_PANDAS_DATAFRAME_NAMES,
        LITERAL_NUMPY_ARRAY_NAMES,
        LITERAL_LIST_OBJECT_NAMES,
    ] = "pd",
) -> Optional[Union[psDataFrame, pdDataFrame, npArray, list]]:
    """
    !!! note "Summary"
        Retrieve the values from a specified column in a `pyspark` dataframe.

    Params:
        dataframe (psDataFrame):
            The DataFrame to retrieve the column values from.
        column (str):
            The column to retrieve the values from.
        distinct (bool, optional):
            Whether to retrieve only distinct values.<br>
            Defaults to `#!py True`.
        return_type (Union[LITERAL_PYSPARK_DATAFRAME_NAMES, LITERAL_PANDAS_DATAFRAME_NAMES, LITERAL_NUMPY_ARRAY_NAMES, LITERAL_LIST_OBJECT_NAMES], optional):
            The type of object to return.<br>
            Defaults to `#!py "pd"`.

    Raises:
        TypeError:
            If any of the inputs parsed to the parameters of this function are not the correct type. Uses the [`@typeguard.typechecked`](https://typeguard.readthedocs.io/en/stable/api.html#typeguard.typechecked) decorator.
        ValueError:
            If the `return_type` is not one of the valid options.
        ColumnDoesNotExistError:
            If the `#!py column` does not exist within `#!py dataframe.columns`.

    Returns:
        (Optional[Union[psDataFrame, pdDataFrame, npArray, list]]):
            The values from the specified column in the specified return type.

    ???+ example "Examples"

        ```{.py .python linenums="1" title="Set up"}
        >>> # Imports
        >>> import pandas as pd
        >>> from pyspark.sql import SparkSession
        >>> from toolbox_pyspark.info import get_column_values
        >>>
        >>> # Instantiate Spark
        >>> spark = SparkSession.builder.getOrCreate()
        >>>
        >>> # Create data
        >>> df = spark.createDataFrame(
        ...     pd.DataFrame(
        ...         {
        ...             "a": [1, 2, 3, 4],
        ...             "b": ["a", "b", "c", "d"],
        ...             "c": [1, 1, 1, 1],
        ...             "d": ["2", "3", "3", "3"],
        ...             "e": ["a", "a", "b", "b"],
        ...         }
        ...     )
        ... )
        >>>
        >>> # Check
        >>> df.show()
        ```
        <div class="result" markdown>
        ```{.txt .text title="Terminal"}
        +---+---+---+---+---+
        | a | b | c | d | e |
        +---+---+---+---+---+
        | 1 | a | 1 | 2 | a |
        | 2 | b | 1 | 3 | a |
        | 3 | c | 1 | 3 | b |
        | 4 | d | 1 | 3 | b |
        +---+---+---+---+---+
        ```
        </div>

        ```{.py .python linenums="1" title="Example 1: Retrieve all values as pyspark DataFrame"}
        >>> result = get_column_values(df, "e", distinct=False, return_type="ps")
        >>> result.show()
        ```
        <div class="result" markdown>
        ```{.txt .text title="Terminal"}
        +---+
        | e |
        +---+
        | a |
        | a |
        | b |
        | b |
        +---+
        ```
        !!! success "Conclusion: Successfully retrieved all values as pyspark DataFrame."
        </div>

        ```{.py .python linenums="1" title="Example 2: Retrieve distinct values as pandas DataFrame"}
        >>> result = get_column_values(df, "b", distinct=True, return_type="pd")
        >>> print(result)
        ```
        <div class="result" markdown>
        ```{.txt .text title="Terminal"}
           b
        0  a
        1  b
        2  c
        3  d
        ```
        !!! success "Conclusion: Successfully retrieved distinct values as pandas DataFrame."
        </div>

        ```{.py .python linenums="1" title="Example 3: Retrieve all values as list"}
        >>> result = get_column_values(df, "c", distinct=False, return_type="list")
        >>> print(result)
        ```
        <div class="result" markdown>
        ```{.txt .text title="Terminal"}
        ['1', '1', '1', '1']
        ```
        !!! success "Conclusion: Successfully retrieved all values as list."
        </div>

        ```{.py .python linenums="1" title="Example 4: Retrieve distinct values as numpy array"}
        >>> result = get_column_values(df, "d", distinct=True, return_type="np")
        >>> print(result)
        ```
        <div class="result" markdown>
        ```{.txt .text title="Terminal"}
        ['2' '3']
        ```
        !!! success "Conclusion: Successfully retrieved distinct values as numpy array."
        </div>

        ```{.py .python linenums="1" title="Example 5: Invalid column"}
        >>> result = get_column_values(df, "invalid", distinct=True, return_type="pd")
        ```
        <div class="result" markdown>
        ```{.txt .text title="Terminal"}
        ColumnDoesNotExistError: Column 'invalid' does not exist. Did you mean one of the following? [a, b, c, d, e]
        ```
        !!! failure "Conclusion: Failed to retrieve values due to invalid column."
        </div>

        ```{.py .python linenums="1" title="Example 6: Invalid return type"}
        >>> result = get_column_values(df, "b", distinct=True, return_type="invalid")
        ```
        <div class="result" markdown>
        ```{.txt .text title="Terminal"}
        ValueError: Invalid return type: invalid
        ```
        !!! failure "Conclusion: Failed to retrieve values due to invalid return type."
        </div>

    ??? tip "See Also"
        - [`get_distinct_values`][toolbox_pyspark.info.get_distinct_values]
    """

    assert_column_exists(dataframe, column)

    dataframe = dataframe.select(column)

    if distinct:
        dataframe = dataframe.distinct()

    if return_type in VALID_PYSPARK_DATAFRAME_NAMES:
        return dataframe
    elif return_type in VALID_PANDAS_DATAFRAME_NAMES:
        return dataframe.toPandas()
    elif return_type in VALID_NUMPY_ARRAY_NAMES:
        return dataframe.select(column).toPandas().to_numpy()
    elif return_type in VALID_LIST_OBJECT_NAMES:
        return dataframe.select(column).toPandas()[column].tolist()


@typechecked
def get_distinct_values(
    dataframe: psDataFrame, columns: Union[str, str_collection]
) -> tuple[Any, ...]:
    """
    !!! note "Summary"
        Retrieve the distinct values from a specified column in a `pyspark` dataframe.

    Params:
        dataframe (psDataFrame):
            The DataFrame to retrieve the distinct column values from.
        columns (str):
            The column(s) to retrieve the distinct values from.

    Raises:
        TypeError:
            If any of the inputs parsed to the parameters of this function are not the correct type. Uses the [`@typeguard.typechecked`](https://typeguard.readthedocs.io/en/stable/api.html#typeguard.typechecked) decorator.

    Returns:
        (str_tuple):
            The distinct values from the specified column.

    ???+ example "Examples"

        ```{.py .python linenums="1" title="Set up"}
        >>> import pandas as pd
        >>> from pyspark.sql import SparkSession
        >>> from toolbox_pyspark.info import get_distinct_values
        >>> spark = SparkSession.builder.getOrCreate()
        >>> df = spark.createDataFrame(
        ...     pd.DataFrame(
        ...         {
        ...             "a": [1, 2, 3, 4],
        ...             "b": ["a", "b", "c", "d"],
        ...             "c": [1, 1, 1, 1],
        ...             "d": ["2", "2", "2", "2"],
        ...         }
        ...     )
        ... )
        ```

        ```{.py .python linenums="1" title="Example 1: Retrieve distinct values"}
        >>> result = get_distinct_values(df, "b")
        >>> print(result)
        ```
        <div class="result" markdown>
        ```{.txt .text title="Terminal"}
        ('a', 'b', 'c', 'd')
        ```
        !!! success "Conclusion: Successfully retrieved distinct values."
        </div>

        ```{.py .python linenums="1" title="Example 2: Invalid column"}
        >>> result = get_distinct_values(df, "invalid")
        ```
        <div class="result" markdown>
        ```{.txt .text title="Terminal"}
        AnalysisException: Column 'invalid' does not exist. Did you mean one of the following? [a, b, c, d]
        ```
        !!! failure "Conclusion: Failed to retrieve values due to invalid column."
        </div>

    ??? tip "See Also"
        - [`get_column_values`][toolbox_pyspark.info.extract_column_values]
    """
    columns = [columns] if is_type(columns, str) else columns
    rows: list[T.Row] = dataframe.select(*columns).distinct().collect()
    if len(columns) == 1:
        return tuple(row[columns[0]] for row in rows)
    return tuple(tuple(row[col] for col in columns) for row in rows)
