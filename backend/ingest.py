from sqlalchemy import create_engine, inspect
from schema_types import Table, Column, ForeignKey


def ingest_schema(database_url: str) -> list[Table]:
    engine = create_engine(database_url)
    inspector = inspect(engine)

    tables = []
    for table_name in inspector.get_table_names():
        columns = [
            Column(name=col["name"], type=str(col["type"]))
            for col in inspector.get_columns(table_name)
        ]

        pk_cols = set(inspector.get_pk_constraint(table_name)["constrained_columns"])
        for col in columns:
            if col.name in pk_cols:
                col.is_primary_key = True

        foreign_keys = [
            ForeignKey(
                column=fk["constrained_columns"][0],
                ref_table=fk["referred_table"],
                ref_column=fk["referred_columns"][0],
            )
            for fk in inspector.get_foreign_keys(table_name)
        ]

        tables.append(Table(name=table_name, columns=columns, foreign_keys=foreign_keys))

    return tables