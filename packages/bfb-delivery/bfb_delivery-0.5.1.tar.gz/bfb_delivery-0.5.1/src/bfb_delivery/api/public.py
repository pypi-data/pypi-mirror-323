"""Public functions wrap internal functions which wrap library functions.

This allows separation of API from implementation. It also allows a simplified public API
separate from a more complex internal API with more options for power users.
"""

from pathlib import Path

from typeguard import typechecked

from bfb_delivery.api import internal
from bfb_delivery.lib.constants import Defaults


@typechecked
def split_chunked_route(
    input_path: Path | str,
    output_dir: Path | str = Defaults.SPLIT_CHUNKED_ROUTE["output_dir"],
    output_filename: str = Defaults.SPLIT_CHUNKED_ROUTE["output_filename"],
    n_books: int = Defaults.SPLIT_CHUNKED_ROUTE["n_books"],
    book_one_drivers_file: str = Defaults.SPLIT_CHUNKED_ROUTE["book_one_drivers_file"],
    date: str = Defaults.SPLIT_CHUNKED_ROUTE["date"],
) -> list[Path]:
    """Split route sheet into n workbooks with sheets by driver.

    Sheets by driver allows splitting routes by driver on Circuit upload.
    Multiple workbooks allows team to split the uploads among members, so one person
    doesn't have to upload all routes.
    This process follows the "chunking" process in the route generation, where routes
    are split into smaller "chunks" by driver (i.e., each stop is labeled with a driver).

    Reads a route spreadsheet at `input_path`.
    Writes `n_books` Excel workbooks with each sheet containing the stops for a single driver.
    Writes adjacent to the original workbook unless `output_dir` specified. If specified, will
    create the directory if it doesn't exist.

    .. note::

        Renames "Box Type" column name to "Product Type", per Circuit API.

    .. note::

        The date passed sets the date in the sheet names of the output workbooks, and that
        date in the sheet name is used for the manifest date field in later functions that
        make the manifests: :py:func:`bfb_delivery.api.public.format_combined_routes` and
        :py:func:`bfb_delivery.api.public.create_manifests` (which wraps the former).


    See :doc:`split_chunked_route` for more information.

    Args:
        input_path: Path to the chunked route sheet that this function reads in and splits up.
        output_dir: Directory to save the output workbook.
            Empty string saves to the input `input_path` directory.
        output_filename: Name of the output workbook.
            Empty string sets filename to "split_workbook_{date}_{i of n_books}.xlsx".
        n_books: Number of workbooks to split into.
        book_one_drivers_file: Path to the book-one driver's file. If empty (default), uses
            a constant list. See :py:data:`bfb_delivery.lib.constants.BookOneDrivers`.
        date: The date to use in the output workbook sheetnames. Empty string (default) uses
            the soonest Friday.

    Returns:
        Paths to the split chunked route workbooks.

    Raises:
        ValueError: If `n_books` is less than 1.
        ValueError: If `n_books` is greater than the number of drivers in the input workbook.
    """
    return internal.split_chunked_route(
        input_path=input_path,
        output_dir=output_dir,
        output_filename=output_filename,
        n_books=n_books,
        book_one_drivers_file=book_one_drivers_file,
        date=date,
    )


@typechecked
def create_manifests_from_circuit(
    start_date: str = Defaults.CREATE_MANIFESTS_FROM_CIRCUIT["start_date"],
    end_date: str = Defaults.CREATE_MANIFESTS_FROM_CIRCUIT["end_date"],
    output_dir: str = Defaults.CREATE_MANIFESTS_FROM_CIRCUIT["output_dir"],
    # TODO: Standardize to Path for all i/o except CLI input.
    output_filename: str = Defaults.CREATE_MANIFESTS_FROM_CIRCUIT["output_filename"],
    circuit_output_dir: str = Defaults.CREATE_MANIFESTS_FROM_CIRCUIT["circuit_output_dir"],
    all_hhs: bool = Defaults.CREATE_MANIFESTS_FROM_CIRCUIT["all_hhs"],
    verbose: bool = Defaults.CREATE_MANIFESTS_FROM_CIRCUIT["verbose"],
    extra_notes_file: str = Defaults.CREATE_MANIFESTS_FROM_CIRCUIT["extra_notes_file"],
) -> tuple[Path, Path]:
    """Gets optimized routes from Circuit, creates driver manifest workbook ready to print.

    This is used after uploading and optimizing the routes. Reads routes CSVs from Circuit,
    and creates a formatted workbook with driver manifests ready to print, with headers,
    aggregate data, and color-coded box types. Each driver's route is a separate sheet in the
    workbook.

    The workbook is saved to `output_dir` with the name `output_filename`. Will create
    `output_dir` if it doesn't exist.

    .. note::

        Uses the date of the front of each CSV name to set the manifest date field. I.e.,
        each sheet should be named something like "08.08 Richard N", and, e.g., this would
        set the manifest date field to "Date: 08.08". **But, this does not determine the
        search date range.**

    Wraps :py:func:`bfb_delivery.api.public.create_manifests` and adds Circuit integration.
    And, `create_manifests` just wraps :py:func:`bfb_delivery.api.public.combine_route_tables`
    and :py:func:`bfb_delivery.api.public.format_combined_routes`. Creates an intermediate
    output workbook with all routes combined, then formats it.

    See :doc:`create_manifests_from_circuit` for more information.

    Args:
        start_date: The start date to use in the output workbook sheetnames as "YYYYMMDD".
            Empty string (default) uses the soonest Friday. Range is inclusive.
        end_date: The end date to use in the output workbook sheetnames as "YYYYMMDD".
            Empty string (default) uses the start date. Range is inclusive.
        output_dir: The directory to write the formatted manifest workbook to.
            Empty string (default) saves to the `input_dir` directory.
        output_filename: The name of the output workbook.
            Empty string (default) sets filename to "final_manifests_{date}.xlsx".
        circuit_output_dir: The directory to create a subdir to save the routes to.
            Creates "routes_{date}" directory within the `circuit_output_dir`.
            Empty string uses `output_dir`.
            If the directory does not exist, it is created. If it exists, it is overwritten.
        all_hhs: Flag to get only the "All HHs" route.
            False gets all routes except "All HHs". True gets only the "All HHs" route.
            NOTE: True returns email column in CSV, for reuploading after splitting.
        verbose: Flag to print verbose output.
        extra_notes_file: Path to the extra notes file. If empty (default), uses a constant
            DataFrame. See :py:data:`bfb_delivery.lib.constants.ExtraNotes`.

    Returns:
        Path to the final manifest workbook.
    """
    final_manifest_path, new_circuit_output_dir = internal.create_manifests_from_circuit(
        start_date=start_date,
        end_date=end_date,
        output_dir=output_dir,
        output_filename=output_filename,
        circuit_output_dir=circuit_output_dir,
        all_hhs=all_hhs,
        verbose=verbose,
        extra_notes_file=extra_notes_file,
    )

    return final_manifest_path, new_circuit_output_dir


@typechecked
def create_manifests(
    input_dir: Path | str,
    output_dir: Path | str = Defaults.CREATE_MANIFESTS["output_dir"],
    output_filename: str = Defaults.CREATE_MANIFESTS["output_filename"],
    extra_notes_file: str = Defaults.CREATE_MANIFESTS["extra_notes_file"],
) -> Path:
    """From Circuit route CSVs, creates driver manifest workbook ready to print.

    This is used after optimizing and exporting the routes to individual CSVs. Reads in
    driver route CSVs from `input_dir` and creates a formatted workbook with driver
    manifests ready to print, with headers, aggregate data, and color-coded box types. Each
    driver's route is a separate sheet in the workbook.

    The workbook is saved to `output_dir` with the name `output_filename`. Will create
    `output_dir` if it doesn't exist.

    .. note::

        Uses the date of the front of each CSV name to set the manifest date field. I.e.,
        each sheet should be named something like "08.08 Richard N", and, e.g., this would
        set the manifest date field to "Date: 08.08".

    Just wraps :py:func:`bfb_delivery.api.public.combine_route_tables` and
    :py:func:`bfb_delivery.api.public.format_combined_routes`. Creates an intermediate output
    workbook with all routes combined, then formats it.

    See :doc:`create_manifests` for more information.

    Args:
        input_dir: The directory containing the driver route CSVs.
        output_dir: The directory to write the formatted manifest workbook to.
            Empty string (default) saves to the `input_dir` directory.
        output_filename: The name of the output workbook.
            Empty string sets filename to "final_manifests_{date}.xlsx".
        extra_notes_file: Path to the extra notes file. If empty (default), uses a constant
            DataFrame. See :py:data:`bfb_delivery.lib.constants.ExtraNotes`.

    Returns:
        Path to the formatted manifest workbook.
    """
    formatted_manifest_path = internal.create_manifests(
        input_dir=input_dir,
        output_dir=output_dir,
        output_filename=output_filename,
        extra_notes_file=extra_notes_file,
    )

    return formatted_manifest_path


@typechecked
def combine_route_tables(
    input_dir: Path | str,
    output_dir: Path | str = Defaults.COMBINE_ROUTE_TABLES["output_dir"],
    output_filename: str = Defaults.COMBINE_ROUTE_TABLES["output_filename"],
) -> Path:
    """Combines the driver route CSVs into a single workbook.

    This is used after optimizing and exporting the routes to individual CSVs. It prepares the
    worksheets to be formatted with :py:func:`bfb_delivery.api.public.format_combined_routes`.

    If `output_dir` is specified, will create the directory if it doesn't exist.

    .. note::

        Changes "Product Type" column name back to "Box Type".

    See :doc:`combine_route_tables` for more information.

    Args:
        input_dir: The directory containing the driver route CSVs.
        output_dir: The directory to write the output workbook to.
            Empty string (default) saves to the `input_dir` directory.
        output_filename: The name of the output workbook.
            Empty string (default) will name the file "combined_routes_{date}.xlsx".

    Returns:
        The path to the output workbook.

    Raises:
        ValueError: If `input_paths` is empty.
    """
    return internal.combine_route_tables(
        input_dir=input_dir, output_dir=output_dir, output_filename=output_filename
    )


@typechecked
def format_combined_routes(
    input_path: Path | str,
    output_dir: Path | str = Defaults.FORMAT_COMBINED_ROUTES["output_dir"],
    output_filename: str = Defaults.FORMAT_COMBINED_ROUTES["output_filename"],
    extra_notes_file: str = Defaults.FORMAT_COMBINED_ROUTES["extra_notes_file"],
) -> Path:
    """Formats the combined routes table into driver manifests to print.

    Adds headers and aggregate data. Color codes box types.

    This is used after combining the driver route CSVs into a single workbook
    using :py:func:`bfb_delivery.api.public.combine_route_tables`.

    If `output_dir` is specified, will create the directory if it doesn't exist.

    .. note::

        Uses the date of the front of each sheet name to set the manifest date field. I.e.,
        each sheet should be named something like "05.27 Oscar W", and, e.g., this would set
        the manifest date field to "Date: 05.27".

    See :doc:`format_combined_routes` for more information.

    Args:
        input_path: The path to the combined routes table.
        output_dir: The directory to write the formatted table to.
            Empty string (default) saves to the input path's parent directory.
        output_filename: The name of the formatted workbook.
            Empty string (default) will name the file "formatted_routes_{date}.xlsx".
        extra_notes_file: The path to the extra notes file. If empty (default), uses a
            constant DataFrame. See :py:data:`bfb_delivery.lib.constants.ExtraNotes`.

    Returns:
        The path to the formatted table.
    """
    return internal.format_combined_routes(
        input_path=input_path,
        output_dir=output_dir,
        output_filename=output_filename,
        extra_notes_file=extra_notes_file,
    )
