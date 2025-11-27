import { useState, useRef, useEffect } from 'react'
import './ChatWindow.css'

function ChatWindow({ messages, onSendMessage, loading }) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (input.trim() && !loading) {
      onSendMessage(input.trim())
      setInput('')
    }
  }

  return (
    <div className="chat-window">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <h2>Welcome to Cape Town Chat</h2>
            <p>Ask me anything about Cape Town and the Western Cape!</p>
            <p>Try questions like:</p>
            <ul>
              <li>"What are the best wine regions near Cape Town?"</li>
              <li>"Tell me about Table Mountain"</li>
              <li>"What is there to do in the Garden Route?"</li>
            </ul>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-content">
                <span className="message-role">
                  {msg.role === 'user' ? 'You' : 'Assistant'}
                </span>
                <p>{msg.content}</p>

                {msg.rag_sources && msg.rag_sources.length > 0 && (
                  <div className="rag-sources">
                    <span className="sources-label">Sources used:</span>
                    {msg.rag_sources.map((source, i) => (
                      <div key={i} className="source-item">
                        <span className="source-score">
                          {(source.score * 100).toFixed(0)}% match
                        </span>
                        <span className="source-text">
                          {source.text.substring(0, 150)}...
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="message assistant">
            <div className="message-content">
              <span className="typing-indicator">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about Cape Town..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  )
}

export default ChatWindow
