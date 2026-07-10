import { Handle, Position } from 'reactflow';

function TableNode({ data }) {
  return (
    <div className="table-node">
      <Handle type="target" position={Position.Left} />
      <div className="table-node-header">{data.name}</div>
      {data.columns.map((col) => (
        <div key={col.name} className="table-node-row">
          <span className="col-name">{col.name}</span>
          <span className="col-type">{col.type}</span>
          {col.is_primary_key && <span className="badge pk">PK</span>}
          {data.fkColumns.includes(col.name) && <span className="badge fk">FK</span>}
        </div>
      ))}
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

export default TableNode;