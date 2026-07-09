import { useState } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [results, setResults] = useState(null);

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
    } else {
      setMessages((prev) => [...prev, { role: 'assistant', text: data.message || data.reason }]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') sendQuestion();
  };

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
        {!results && <p>Results will appear here.</p>}
        {results && results.length === 0 && <p>No results.</p>}
        {results && results.length > 0 && (
          <table>
            <thead>
              <tr>
                {Object.keys(results[0]).map((col) => (
                  <th key={col}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {results.map((row, i) => (
                <tr key={i}>
                  {Object.values(row).map((val, j) => (
                    <td key={j}>{String(val)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default App;