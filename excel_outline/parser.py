from __future__ import annotations

from pathlib import Path
from typing import Any

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter


def parse_workbook(path: str | Path) -> dict[str, Any]:
    """
    Parse a workbook into a compact JSON-like outline.

    Current scope:
    - .xlsx only
    - supports simple 2-column "map" sheets like the Input fixture
    - supports simple formula tables with integer-range columns like the Output fixture

    The goal is not to serialize every populated cell. The goal is to capture
    the workbook's structural schema in a compact, LLM-friendly way.
    """
    workbook_path = Path(path).expanduser().resolve()

    if workbook_path.suffix.lower() != ".xlsx":
        raise ValueError(f"Only .xlsx files are supported: {workbook_path}")
    if not workbook_path.exists():
        raise FileNotFoundError(f"Workbook not found: {workbook_path}")

    # data_only=False is important because we need the raw formulas,
    # not just cached computed values.
    wb = load_workbook(workbook_path, data_only=False)

    sheets_out: list[dict[str, Any]] = []

    # Keep track of detected maps so formula rows in later sheets can
    # recognize references like Input!$B$2 -> variable "a".
    known_maps: dict[str, dict[str, dict[str, Any]]] = {}

    # First pass: detect map sheets
    parsed_sheet_names: set[str] = set()

    for ws in wb.worksheets:
        map_element = detect_map_sheet(ws)
        if map_element is not None:
            sheets_out.append(
                {
                    "name": ws.title,
                    "elements": [map_element],
                }
            )
            parsed_sheet_names.add(ws.title)

            # Build a lookup that helps formula inference later.
            map_lookup: dict[str, dict[str, Any]] = {}
            for key, entry in map_element["entries"].items():
                value_anchor = entry["value_anchor"]   # e.g. "Input!B2"
                value_cell = value_anchor.split("!", 1)[1]  # e.g. "B2"
                map_lookup[key] = {
                    "anchor": entry["anchor"],
                    "value_anchor": value_anchor,
                    "value_cell": value_cell,
                    "value": entry["value"],
                }

            known_maps[ws.title] = map_lookup

    # Second pass: detect table sheets
    for ws in wb.worksheets:
        if ws.title in parsed_sheet_names:
            continue

        table_element = detect_table_sheet(ws, known_maps)
        if table_element is not None:
            sheets_out.append(
                {
                    "name": ws.title,
                    "elements": [table_element],
                }
            )
            parsed_sheet_names.add(ws.title)
        else:
            # Optional fallback:
            # You could either skip unsupported sheets or include an empty entry.
            # For now, include an empty elements list so callers still see the sheet.
            sheets_out.append(
                {
                    "name": ws.title,
                    "elements": [],
                }
            )

    return {"sheets": sheets_out}


def detect_map_sheet(ws: Worksheet) -> dict[str, Any] | None:
    """
    Detect a simple 2-column key/value sheet like:

        A1: var      B1: value
        A2: a        B2: 3
        A3: b        B3: 4

    Returns a single "map" element dict if matched, otherwise None.
    """
    if ws.max_row < 2 or ws.max_column < 2:
        return None

    # Require header cells at A1 and B1.
    if ws["A1"].value is None or ws["B1"].value is None:
        return None

    entries: dict[str, dict[str, Any]] = {}

    # Require data rows from row 2 onward:
    # - column A: string-ish key
    # - column B: literal value, not a formula
    for row in range(2, ws.max_row + 1):
        key_cell = ws[f"A{row}"]
        value_cell = ws[f"B{row}"]

        key = key_cell.value
        value = value_cell.value

        # Stop if we hit a blank row in the primary region.
        if key is None and value is None:
            continue

        if not isinstance(key, str) or key.strip() == "":
            return None

        if isinstance(value, str) and value.startswith("="):
            return None

        entries[key] = {
            "anchor": make_anchor(ws.title, key_cell.coordinate),
            "value_anchor": make_anchor(ws.title, value_cell.coordinate),
            "value": value,
        }

    if not entries:
        return None

    return {
        "kind": "map",
        "anchor": make_anchor(ws.title, "A1"),
        "entries": entries,
    }


def detect_table_sheet(
    ws: Worksheet,
    known_maps: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any] | None:
    """
    Detect a simple table sheet like the Output fixture:

        A1 = "series"
        B1:K1 = 1..10
        A2:A4 = series names
        B2:K4 = formulas

    Returns a single "table" element dict if matched, otherwise None.
    """
    if ws.max_row < 2 or ws.max_column < 3:
        return None

    if ws["A1"].value is None:
        return None

    # Detect header values in row 1 from B1 to last used column.
    header_values = []
    for col in range(2, ws.max_column + 1):
        header_values.append(ws.cell(row=1, column=col).value)

    columns_info = detect_integer_range(
        sheet_name=ws.title,
        start_col=2,
        end_col=ws.max_column,
        values=header_values,
    )
    if columns_info is None:
        return None

    series: dict[str, dict[str, Any]] = {}

    # Parse each row after the header.
    for row in range(2, ws.max_row + 1):
        label = ws.cell(row=row, column=1).value
        if not isinstance(label, str) or label.strip() == "":
            return None

        formula_cells = [ws.cell(row=row, column=col) for col in range(2, ws.max_column + 1)]

        # Require all cells in the data range to be formulas for this simple version.
        if not all(isinstance(cell.value, str) and cell.value.startswith("=") for cell in formula_cells):
            return None

        rule_info = infer_series_rule(
            ws=ws,
            row=row,
            start_col=2,
            end_col=ws.max_column,
            known_maps=known_maps,
        )
        if rule_info is None:
            return None

        start_coord = ws.cell(row=row, column=2).coordinate
        end_coord = ws.cell(row=row, column=ws.max_column).coordinate

        series[label] = {
            "anchor": make_anchor(ws.title, f"A{row}"),
            "range": f"{ws.title}!{start_coord}:{end_coord}",
            "rule": rule_info["rule"],
            "depends_on": rule_info["depends_on"],
        }

    return {
        "kind": "table",
        "anchor": make_anchor(ws.title, "A1"),
        "columns": columns_info,
        "series": series,
    }


def detect_integer_range(
    sheet_name: str,
    start_col: int,
    end_col: int,
    values: list[Any],
) -> dict[str, Any] | None:
    """
    Detect a row of integers forming an arithmetic progression.
    Example: [1,2,3,...,10]
    """
    if not values:
        return None

    if not all(isinstance(v, int) for v in values):
        return None

    if len(values) == 1:
        step = 1
    else:
        step = values[1] - values[0]
        if step == 0:
            return None
        for i in range(2, len(values)):
            if values[i] - values[i - 1] != step:
                return None

    start_coord = f"{get_column_letter(start_col)}1"
    end_coord = f"{get_column_letter(end_col)}1"

    return {
        "anchor": f"{sheet_name}!{start_coord}",
        "range": f"{sheet_name}!{start_coord}:{end_coord}",
        "kind": "integer_range",
        "start": values[0],
        "end": values[-1],
        "step": step,
    }


def infer_series_rule(
    ws: Worksheet,
    row: int,
    start_col: int,
    end_col: int,
    known_maps: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any] | None:
    """
    Infer a compact rule for a series row.

    Current supported patterns:
    1. column * variable
       Example:
         B2 = B$1*Input!$B$2
         C2 = C$1*Input!$B$2

    2. series_a + series_b
       Example:
         B4 = B2+B3
         C4 = C2+C3
    """
    formulas = []
    for col in range(start_col, end_col + 1):
        value = ws.cell(row=row, column=col).value
        if not isinstance(value, str) or not value.startswith("="):
            return None
        formulas.append(value)

    # Try pattern 1: column * map-variable
    column_times_variable = try_infer_column_times_variable(
        ws=ws,
        row=row,
        start_col=start_col,
        end_col=end_col,
        formulas=formulas,
        known_maps=known_maps,
    )
    if column_times_variable is not None:
        return column_times_variable

    # Try pattern 2: same-column sum of two prior series rows
    row_sum = try_infer_row_sum(
        ws=ws,
        row=row,
        start_col=start_col,
        end_col=end_col,
        formulas=formulas,
    )
    if row_sum is not None:
        return row_sum

    return None


def try_infer_column_times_variable(
    ws: Worksheet,
    row: int,
    start_col: int,
    end_col: int,
    formulas: list[str],
    known_maps: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any] | None:
    """
    Match formulas like:
        =B$1*Input!$B$2
        =C$1*Input!$B$2
        ...

    We detect:
    - one factor changes with the column header cell
    - one factor stays fixed and points to an input map value cell
    """
    fixed_variable_name: str | None = None
    fixed_sheet_name: str | None = None

    for offset, col in enumerate(range(start_col, end_col + 1)):
        formula = formulas[offset]
        body = formula[1:]  # remove leading '='

        parts = body.split("*")
        if len(parts) != 2:
            return None

        left, right = parts[0].strip(), parts[1].strip()

        expected_header_ref_a = f"{get_column_letter(col)}$1"
        expected_header_ref_b = f"${get_column_letter(col)}$1"

        # One side should be the current column header ref.
        if left in {expected_header_ref_a, expected_header_ref_b}:
            other = right
        elif right in {expected_header_ref_a, expected_header_ref_b}:
            other = left
        else:
            return None

        normalized_other = normalize_excel_ref(other)

        # See if that fixed ref matches one of the known map value cells.
        matched = lookup_variable_by_value_ref(normalized_other, known_maps)
        if matched is None:
            return None

        sheet_name, variable_name = matched

        if fixed_variable_name is None:
            fixed_variable_name = variable_name
            fixed_sheet_name = sheet_name
        else:
            if variable_name != fixed_variable_name or sheet_name != fixed_sheet_name:
                return None

    assert fixed_variable_name is not None
    assert fixed_sheet_name is not None

    return {
        "rule": f"column * {fixed_variable_name}",
        "depends_on": [f"{fixed_sheet_name}.{fixed_variable_name}", "column"],
    }


def try_infer_row_sum(
    ws: Worksheet,
    row: int,
    start_col: int,
    end_col: int,
    formulas: list[str],
) -> dict[str, Any] | None:
    """
    Match formulas like:
        =B2+B3
        =C2+C3
        ...

    That becomes:
        rule = "a + b"
        depends_on = ["a", "b"]
    """
    referenced_rows: tuple[int, int] | None = None

    for offset, col in enumerate(range(start_col, end_col + 1)):
        formula = formulas[offset]
        body = formula[1:]  # remove '='
        parts = body.split("+")
        if len(parts) != 2:
            return None

        left, right = parts[0].strip(), parts[1].strip()

        expected_left_col = get_column_letter(col)

        left_col, left_row = split_a1_ref(normalize_excel_ref(left))
        right_col, right_row = split_a1_ref(normalize_excel_ref(right))

        # Both references must point to the same current column.
        if left_col != expected_left_col or right_col != expected_left_col:
            return None

        current_pair = (left_row, right_row)
        if referenced_rows is None:
            referenced_rows = current_pair
        else:
            if current_pair != referenced_rows:
                return None

    assert referenced_rows is not None
    row1, row2 = referenced_rows

    label1 = ws.cell(row=row1, column=1).value
    label2 = ws.cell(row=row2, column=1).value

    if not isinstance(label1, str) or not isinstance(label2, str):
        return None

    return {
        "rule": f"{label1} + {label2}",
        "depends_on": [label1, label2],
    }


def lookup_variable_by_value_ref(
    normalized_ref: str,
    known_maps: dict[str, dict[str, dict[str, Any]]],
) -> tuple[str, str] | None:
    """
    Given a normalized ref like 'Input!B2', return ('Input', 'a') if that
    cell is known to be the value cell for Input.a.
    """
    if "!" not in normalized_ref:
        return None

    sheet_name, cell_ref = normalized_ref.split("!", 1)

    if sheet_name not in known_maps:
        return None

    for variable_name, info in known_maps[sheet_name].items():
        if info["value_cell"] == cell_ref:
            return sheet_name, variable_name

    return None


def normalize_excel_ref(ref: str) -> str:
    """
    Normalize refs by removing dollar signs.
    Example:
        'Input!$B$2' -> 'Input!B2'
        '$C$1' -> 'C1'
    """
    return ref.replace("$", "")


def split_a1_ref(ref: str) -> tuple[str, int]:
    """
    Split 'B12' into ('B', 12).
    Assumes a simple valid A1 reference with no sheet prefix.
    """
    letters = []
    digits = []

    for ch in ref:
        if ch.isalpha():
            letters.append(ch)
        elif ch.isdigit():
            digits.append(ch)

    if not letters or not digits:
        raise ValueError(f"Invalid A1 reference: {ref}")

    return "".join(letters), int("".join(digits))


def make_anchor(sheet_name: str, coordinate: str) -> str:
    return f"{sheet_name}!{coordinate}"