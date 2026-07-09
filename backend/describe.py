

def generate_description(table) -> str:
    # columns: name + type, comma-separated
    col_text = ", ".join(f"{c.name} ({c.type})" for c in table.columns)

    # FKs: "this column -> ref_table.ref_column", comma-separated (or "none" if no FKs)
    if table.foreign_keys:
        fk_text = ", ".join(
            f"{fk.column} -> {fk.ref_table}.{fk.ref_column}" for fk in table.foreign_keys
        )
    else:
        fk_text = "none"
        
    # static templated purpose line — placeholder until LLM-generated version replaces it
    purpose = f"Stores records related to {table.name}."

    return (
        f"Table: {table.name}\n"
        f"Columns: {col_text}\n"
        f"Foreign keys: {fk_text}\n"
        f"Purpose: {purpose}"
    )