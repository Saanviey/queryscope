from sqlglot import exp

#check if tables parsed from AST actually exist in db
def validate_tables_exist(parsed, tables: list) -> list[str]:
    valid_names = {t.name for t in tables}
    parsed_tables = parsed.find_all(exp.Table)

    missing = [pt.name for pt in parsed_tables if pt.name not in valid_names]
    return missing

#check if the statement is "select" type only (drop/update etc not allowed user can only view the data not modify it)
def validate_is_select(parsed) -> bool:
    return isinstance(parsed, exp.Select)


#each exp.Table node has both .name (real table name) and .alias
#Build an alias→realname map by walking exp.Table nodes: 
def build_alias_map(parsed) -> dict:
    alias_map = {}
    for table in parsed.find_all(exp.Table):
        alias = table.alias or table.name  #map name to itself if no alias
        alias_map[alias] = table.name
    return alias_map

# validate columns using alias map resolution
def validate_columns_exist(parsed, tables: list) -> list[str]:
    alias_map = build_alias_map(parsed)
    columns_by_table = {t.name: {c.name for c in t.columns} for t in tables}
    query_tables = set(alias_map.values())

    # collect column/expression aliases the query itself defines (e.g. COUNT(*) AS num_tickets)
    # these are valid to reference later (ORDER BY, GROUP BY, HAVING) even though they're not real schema columns
    select_aliases = {a.alias for a in parsed.find_all(exp.Alias) if a.alias}

    missing = []
    seen = set()  # dedupes repeated flags for the same column (e.g. same ambiguous col in WHERE and JOIN)

    for col in parsed.find_all(exp.Column):
        if col.table:
            real_table = alias_map.get(col.table, col.table)
            if col.name not in columns_by_table.get(real_table, set()):
                key = f"{real_table}.{col.name}"
                if key not in seen:
                    missing.append(key)
                    seen.add(key)
        else:
            if col.name in select_aliases:
                continue  # reference to a query-defined alias, not a hallucination — skip entirely

            matches = [t for t in query_tables if col.name in columns_by_table.get(t, set())]
            if len(matches) == 0:
                key = f"{col.name} (not found in any queried table)"
                if key not in seen:
                    missing.append(key)
                    seen.add(key)
            elif len(matches) > 1:
                key = f"{col.name} (ambiguous — exists in {sorted(matches)})"
                if key not in seen:
                    missing.append(key)
                    seen.add(key)

    return missing