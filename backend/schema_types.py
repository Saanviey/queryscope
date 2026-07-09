from dataclasses import dataclass, field

@dataclass
class ForeignKey:
    column: str        # the column in THIS table holding the foreign key
    ref_table: str     #  the table being pointed TO
    ref_column: str    # the column in that other table being pointed to

#Column represents one column in a table — name, its SQL type, and whether it's a PK.
@dataclass
class Column:
    name: str                         
    type: str                          
                                      
    is_primary_key: bool = False       # defaults to False; inspect() gives PKs separately
                                       
# Table represents one full table: its name, its columns, and its FK relationships.
@dataclass
class Table:
    name: str
    columns: list[Column] = field(default_factory=list)
    foreign_keys: list[ForeignKey] = field(default_factory=list)

