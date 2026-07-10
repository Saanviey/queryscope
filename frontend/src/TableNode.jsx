function TableNode({ data }) {
  return (
    <div className="table-node">
      <div className="table-node-header">{data.name}</div>
      {data.columns.map((col) => (
        <div key={col.name} className="table-node-row">
          <span className="col-name">{col.name}</span>
          <span className="col-type">{col.type}</span>
          {col.is_primary_key && <span className="badge pk">PK</span>}
          {data.fkColumns.includes(col.name) && <span className="badge fk">FK</span>}
        </div>
      ))}
    </div>
  );
}

export default TableNode;