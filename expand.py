


def expand_with_fks(retrieved_table_names: list[str], all_tables: list) -> set[str]:
    # build a name -> Table lookup, so we can go from a string to the actual object
    table_by_name = {t.name: t for t in all_tables}

    expanded = set(retrieved_table_names)  # start with what retrieval already found

    for name in retrieved_table_names:
        table = table_by_name[name]

        # outgoing: this table's own FKs point directly to other tables
        for fk in table.foreign_keys:
            expanded.add(fk.ref_table)

        # incoming: scan every other table, check if any of ITS FKs point back at this one
        for other in all_tables:
            for fk in other.foreign_keys:
                if fk.ref_table == name:
                    expanded.add(other.name)

    return expanded