import React, { useState } from 'react';

function App() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState([]);

  const API_BASE = 'http://localhost:8000';

  const addLog = (msg) => setLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), msg }]);

  // ===== FIXED: Uses POST instead of GET =====
  const sendChat = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setResponse('');

    try {
      const res = await fetch(`${API_BASE}/api/v1/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt })
      });
      
      const data = await res.json();
      
      // Handle errors from backend
      if (data.detail) {
        setResponse(`❌ Error: ${data.detail}`);
        addLog(`❌ Chat error: ${data.detail}`);
        setLoading(false);
        return;
      }

      const cost = data.cost !== undefined ? data.cost : 0;
      const tokens = data.tokens !== undefined ? data.tokens : 0;
      const latency = data.latency_ms !== undefined ? data.latency_ms : 0;

      setResponse(`
🤖 Response: ${data.response || 'No response'}
Model: ${data.model || 'unknown'} (${data.provider || 'unknown'})
Tokens: ${tokens}
Cost: $${cost.toFixed(6)}
Latency: ${latency.toFixed(0)}ms
      `);
      
      addLog(`✅ Chat: "${prompt.slice(0, 30)}..." → ${data.model || 'unknown'} ($${cost.toFixed(6)})`);
    } catch (err) {
      setResponse(`❌ Error: ${err.message}`);
      addLog(`❌ Chat error: ${err.message}`);
    }
    setLoading(false);
  };

  const testRouter = async () => {
    const tasks = [
      { prompt: "Explain quantum computing", task: "simple" },
      { prompt: "Write Python code to sort a list", task: "coding" },
    ];
    
    for (const t of tasks) {
      try {
        const res = await fetch(`${API_BASE}/api/v1/router/route`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: t.prompt, task_type: t.task })
        });
        const data = await res.json();
        addLog(`🧠 Router: "${t.prompt.slice(0, 20)}..." → ${data.provider}/${data.model}`);
      } catch (err) {
        addLog(`❌ Router error: ${err.message}`);
      }
    }
  };

  const sendTraces = async () => {
    for (let i = 0; i < 5; i++) {
      const trace = {
        trace_id: `trace-${Date.now()}-${i}`,
        span_id: `span-${i}`,
        name: `test-${i}`,
        model: ['gpt-4o-mini', 'llama-3.3-70b-versatile'][i % 2],
        provider: ['openai', 'groq'][i % 2],
        token_usage: { prompt_tokens: 50, completion_tokens: 30, total_tokens: 80 },
        cost: 0.0001 + Math.random() * 0.001,
        start_time: new Date().toISOString(),
        end_time: new Date().toISOString(),
        latency_ms: 200 + Math.random() * 300,
        status: 'success'
      };
      
      try {
        await fetch(`${API_BASE}/api/v1/ingest`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(trace)
        });
        addLog(`📤 Trace ${i+1}: ${trace.model} - $${trace.cost.toFixed(4)}`);
      } catch (err) {
        addLog(`❌ Trace error: ${err.message}`);
      }
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '20px', fontFamily: 'Arial' }}>
      <h1>🔮 ARGUS - REAL AI Observability</h1>
      <p style={{ color: '#666' }}>Actually calls Groq/OpenAI APIs</p>

      <div style={{ display: 'flex', gap: '10px', margin: '20px 0', flexWrap: 'wrap' }}>
        <button onClick={testRouter} style={btn}>🧠 Test Router</button>
        <button onClick={sendTraces} style={{...btn, background: '#4CAF50'}}>📤 Send Traces</button>
      </div>

      <div style={{ border: '1px solid #ddd', padding: '20px', borderRadius: '8px', margin: '20px 0' }}>
        <h3>💬 Chat with LLM</h3>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Ask something to Groq/OpenAI..."
          style={{ width: '100%', minHeight: '80px', padding: '10px', fontSize: '16px' }}
        />
        <button onClick={sendChat} disabled={loading} style={{...btn, marginTop: '10px'}}>
          {loading ? '⏳ Sending...' : '🚀 Send'}
        </button>
        {response && (
          <pre style={{ background: '#f5f5f5', padding: '15px', borderRadius: '8px', marginTop: '10px', whiteSpace: 'pre-wrap' }}>
            {response}
          </pre>
        )}
      </div>

      <div style={{ border: '1px solid #ddd', padding: '20px', borderRadius: '8px' }}>
        <h3>📋 Activity Log</h3>
        <div style={{ maxHeight: '200px', overflow: 'auto', background: '#1a1a2e', padding: '15px', borderRadius: '8px' }}>
          {logs.length === 0 ? (
            <div style={{ color: '#666' }}>No activity yet</div>
          ) : (
            logs.map((log, i) => (
              <div key={i} style={{ color: '#69db7c', fontSize: '13px', fontFamily: 'monospace' }}>
                [{log.time}] {log.msg}
              </div>
            ))
          )}
        </div>
        <button onClick={() => setLogs([])} style={{...btn, background: '#dc3545', marginTop: '10px'}}>Clear</button>
      </div>
    </div>
  );
}

const btn = {
  padding: '10px 20px',
  border: 'none',
  borderRadius: '8px',
  background: '#4F46E5',
  color: 'white',
  fontSize: '14px',
  cursor: 'pointer'
};

export default App;