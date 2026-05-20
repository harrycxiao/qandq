#read and write functions to the Postgres database that API endpoints will call
import json
import psycopg2


DB_CONFIG = {
    "dbname": "llm_pipeline",
    "user": "postgres",
    "password": "H@T$&COCn1",  # replace locally before running
    "host": "localhost",
    "port": 5432,
}


def get_connection():
    """Create a new connection to Postgres."""
    return psycopg2.connect(**DB_CONFIG)


def list_records():
    """Return basic metadata for all stored JSON records."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, source_file, created_at, updated_at
        FROM json_records
        ORDER BY id;
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": row[0],
            "name": row[1],
            "source_file": row[2],
            "created_at": row[3],
            "updated_at": row[4],
        }
        for row in rows
    ]


def get_record_by_name(name):
    """Return the full JSON data for one record, like Input or Output."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT data
        FROM json_records
        WHERE name = %s;
    """, (name,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row is None:
        return None

    return row[0]


def save_record_by_name(name, data):
    """Save a modified JSON object back into Postgres."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE json_records
        SET data = %s,
            updated_at = NOW()
        WHERE name = %s;
    """, (json.dumps(data), name))

    conn.commit()

    cur.close()
    conn.close()


def get_input_values():
    """
    Return clean input values from the Input JSON.

    Example:
    {"a": 3, "b": 4}
    """
    input_data = get_record_by_name("Input")

    if input_data is None:
        return {}

    entries = input_data["elements"][0]["entries"]

    return {
        key: entry["value"]
        for key, entry in entries.items()
    }


def update_input_value(key, value):
    """
    Update one value in the Input JSON.

    Example:
    update_input_value("a", 10)
    """
    input_data = get_record_by_name("Input")

    if input_data is None:
        raise ValueError("Input record not found.")

    entries = input_data["elements"][0]["entries"]

    if key not in entries:
        raise KeyError(f"Input key '{key}' not found.")

    old_value = entries[key]["value"]
    entries[key]["value"] = value

    save_record_by_name("Input", input_data)

    return {
        "key": key,
        "old_value": old_value,
        "new_value": value,
    }


def get_output_values():
    """
    Return clean output values from the Output JSON.

    Example:
    {
        "columns": [1, 2, 3, ..., 10],
        "series": {
            "a": [3, 6, 9, ...],
            "b": [4, 8, 12, ...],
            "c": [7, 14, 21, ...]
        }
    }
    """
    output_data = get_record_by_name("Output")

    if output_data is None:
        return {}

    table = output_data["elements"][0]
    columns = table["columns"].get("values", [])
    series = table["series"]

    return {
        "columns": columns,
        "series": {
            name: details.get("values", [])
            for name, details in series.items()
        }
    }


def recompute_output_values():
    """
    Recalculate Output values from current Input values.

    This updates:
    - columns["values"]
    - each series["values"]

    It does not let the LLM manually edit outputs.
    Outputs are derived from Input + rules.
    """
    input_values = get_input_values()
    output_data = get_record_by_name("Output")

    if output_data is None:
        raise ValueError("Output record not found.")

    table = output_data["elements"][0]
    columns_info = table["columns"]
    series = table["series"]

    start = columns_info["start"]
    end = columns_info["end"]
    step = columns_info["step"]

    columns = list(range(start, end + 1, step))
    columns_info["values"] = columns

    computed = {}

    for series_name, details in series.items():
        rule = details["rule"].strip()

        if rule.startswith("column * "):
            input_key = rule.replace("column * ", "").strip()

            if input_key not in input_values:
                raise KeyError(f"Input key '{input_key}' not found.")

            input_value = input_values[input_key]
            values = [column * input_value for column in columns]

        elif " + " in rule:
            left, right = [part.strip() for part in rule.split("+")]

            if left not in computed or right not in computed:
                raise KeyError(
                    f"Rule '{rule}' depends on series that has not been computed yet."
                )

            values = [
                computed[left][i] + computed[right][i]
                for i in range(len(columns))
            ]

        else:
            raise ValueError(f"Unsupported rule: {rule}")

        details["values"] = values
        computed[series_name] = values

    save_record_by_name("Output", output_data)

    return {
        "columns": columns,
        "series": computed
    }


def update_input_and_recompute(key, value):
    """
    Update one input value, then recompute all derived output values.
    This is the main function your API/LLM should call.
    """
    update_summary = update_input_value(key, value)
    recomputed_outputs = recompute_output_values()

    return {
        "updated_input": update_summary,
        "recomputed_outputs": recomputed_outputs,
    }
