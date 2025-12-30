import React, { useState } from 'react';
import './App.css';

interface RetrievedDoc {
  content: string;
  similarity: number;
  distance: number;
}

interface QueryResponse {
  answer: string;
  retrieved_docs: RetrievedDoc[];
}

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setResponse(null);

    try {
      const res = await fetch('http://localhost:5000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query.trim() }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data: QueryResponse = await res.json();
      setResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '查询失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>🤖 企业知识助手</h1>
          <p>基于 RAG 技术的智能问答系统</p>
        </header>

        <form onSubmit={handleSubmit} className="query-form">
          <div className="input-group">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="请输入您的问题，例如：我工作3年了，可以休假几天？"
              className="query-input"
              rows={3}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="submit-btn"
            >
              {loading ? '查询中...' : '提交查询'}
            </button>
          </div>
        </form>

        {error && (
          <div className="error-message">
            <strong>错误：</strong> {error}
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>正在处理您的查询，请稍候...</p>
          </div>
        )}

        {response && (
          <div className="response-section">
            <div className="answer-card">
              <h2>💬 回答</h2>
              <div className="answer-content">
                {response.answer.split('\n').map((line, index) => (
                  <p key={index}>{line}</p>
                ))}
              </div>
            </div>

            {response.retrieved_docs && response.retrieved_docs.length > 0 && (
              <div className="references-card">
                <h2>📚 参考资料</h2>
                <div className="references-list">
                  {response.retrieved_docs.map((doc, index) => (
                    <div key={index} className="reference-item">
                      <div className="reference-header">
                        <span className="reference-number">参考 {index + 1}</span>
                        <span className="similarity-score">
                          相似度: {(doc.similarity * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="reference-content">
                        {doc.content}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
