import { useState, useEffect } from 'react';
import ReactFlow, { Background } from 'reactflow';
import 'reactflow/dist/style.css';
import dagre from 'dagre';
import TableNode from './TableNode';
import './App.css';

const nodeTypes = { tableNode: TableNode };

function buildFlowData(schema) {
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: 'LR', nodesep: 60, ranksep: 150 });
  g.setDefaultEdgeLabel(() => ({}));

  schema.forEach((table) => {
    const height = 40 + table.columns.length * 24; // header + one row per column
    g.setNode(table.name, { width: 220, height });
  });

  const edges = [];
  schema.forEach((table) => {
    table.foreign_keys.forEach((fk) => {
      g.setEdge(table.name, fk.ref_table);
      edges.push({
        id: `${table.name}-${fk.column}-${fk.ref_table}`,
        source: table.name,
        target: fk.ref_table,
      });
    });
  });

  dagre.layout(g);

  const nodes = schema.map((table) => {
    const pos = g.node(table.name);
    const fkColumns = table.foreign_keys.map((fk) => fk.column);
    return {
      id: table.name,
      type: 'tableNode',
      position: { x: pos.x, y: pos.y },
      data: { name: table.name, columns: table.columns, fkColumns },
    };
  });

  return { nodes, edges };
}

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [results, setResults] = useState(null);
  const [view, setView] = useState('results');
  const [schema, setSchema] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/schema')
      .then((res) => res.json())
      .then(setSchema);
  }, []);

  const sendQuestion = async () => {
    if (!input.trim()) return;
    const question = input;
    setMessages((prev) => [...prev, { role: 'user', text: question }]);
    setInput('');

    const response = await fetch('http://localhost:8000/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
    const data = await response.json();

    if (data.type === 'data_question') {
      setMessages((prev) => [...prev, { role: 'assistant', text: `Ran SQL: ${data.sql}` }]);
      setResults(data.results);
      setView('results');
    } else {
      setMessages((prev) => [...prev, { role: 'assistant', text: data.message || data.reason }]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') sendQuestion();
  };

  const flowData = schema ? buildFlowData(schema) : { nodes: [], edges: [] };
  return (
    <div className="app-container">
      <div className="chat-panel">
        <div className="chat-messages">
          {messages.length === 0 && <p>Ask a question about the database.</p>}
          {messages.map((m, i) => (
            <div key={i} className={`message ${m.role}`}>{m.text}</div>
          ))}
        </div>
        <input
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your question..."
        />
      </div>

      <div className="results-panel">
        <div className="view-toggle">
          <button onClick={() => setView('results')} disabled={view === 'results'}>Results</button>
          <button onClick={() => setView('schema')} disabled={view === 'schema'}>Schema</button>
        </div>

        {view === 'results' && (
          <>
            {!results && <p>Results will appear here.</p>}
            {results && results.length === 0 && <p>No results.</p>}
            {results && results.length > 0 && (
              <table>
                <thead>
                  <tr>{Object.keys(results[0]).map((col) => <th key={col}>{col}</th>)}</tr>
                </thead>
                <tbody>
                  {results.map((row, i) => (
                    <tr key={i}>{Object.values(row).map((val, j) => <td key={j}>{String(val)}</td>)}</tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        )}

        {view === 'schema' && (
          <div style={{ height: '90%', border: '1px solid #333' }}>
            <ReactFlow
                  nodes={flowData.nodes}
                  edges={flowData.edges}
                  nodeTypes={nodeTypes}
                  fitView
                  defaultEdgeOptions={{ style: { stroke: '#888', strokeWidth: 1.5 } }}>
  <Background />
</ReactFlow>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;