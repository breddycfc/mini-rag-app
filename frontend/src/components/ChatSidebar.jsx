import './ChatSidebar.css'

function ChatSidebar({ chats, activeChat, onSelectChat, onNewChat, onDeleteChat }) {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>Cape Town Chat</h2>
        <button className="new-chat-btn" onClick={onNewChat}>
          + New Chat
        </button>
      </div>

      <div className="chat-list">
        {chats.length === 0 ? (
          <p className="no-chats">No conversations yet</p>
        ) : (
          chats.map(chat => (
            <div
              key={chat.id}
              className={`chat-item ${activeChat === chat.id ? 'active' : ''}`}
              onClick={() => onSelectChat(chat.id)}
            >
              <div className="chat-item-content">
                <span className="chat-title">{chat.title}</span>
                <span className="chat-meta">{chat.message_count} messages</span>
              </div>
              <button
                className="delete-btn"
                onClick={(e) => {
                  e.stopPropagation()
                  onDeleteChat(chat.id)
                }}
              >
                x
              </button>
            </div>
          ))
        )}
      </div>

      <div className="sidebar-footer">
        <p>Powered by RAG</p>
        <p>Developed by Branden Reddy</p>
      </div>
    </div>
  )
}

export default ChatSidebar
