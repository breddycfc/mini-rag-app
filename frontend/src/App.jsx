/*
  Main App component for the chat interface.
  AI assisted: SSE stream parsing logic was tricky, got help with the buffer handling.
  Built the component structure and state management myself following React patterns.
*/
import { useState, useEffect } from 'react'
import ChatSidebar from './components/ChatSidebar'
import ChatWindow from './components/ChatWindow'
import './App.css'

function App() {
  const [chats, setChats] = useState([])
  const [activeChat, setActiveChat] = useState(null)
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchChats()
  }, [])

  const fetchChats = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/chats')
      const data = await res.json()
      setChats(data.chats)
    } catch (err) {
      console.error('Failed to fetch chats:', err)
    }
  }

  const loadChat = async (chatId) => {
    try {
      const res = await fetch(`http://localhost:8000/api/chats/${chatId}`)
      const data = await res.json()
      setActiveChat(chatId)
      setMessages(data.messages || [])
    } catch (err) {
      console.error('Failed to load chat:', err)
    }
  }

  const createNewChat = async () => {
    setActiveChat(null)
    setMessages([])
  }

  const deleteChat = async (chatId) => {
    try {
      await fetch(`http://localhost:8000/api/chats/${chatId}`, {
        method: 'DELETE'
      })
      fetchChats()
      if (activeChat === chatId) {
        setActiveChat(null)
        setMessages([])
      }
    } catch (err) {
      console.error('Failed to delete chat:', err)
    }
  }

  const sendMessage = async (text) => {
    const userMessage = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMessage])
    setLoading(true)

    let currentContent = ''
    let currentSources = null
    let newChatId = activeChat

    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          chat_id: activeChat
        })
      })

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
        rag_sources: null
      }])
      setLoading(false)

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        const lines = buffer.split('\n')
        buffer = lines.pop()

        for (const line of lines) {
          if (line.startsWith('data:')) {
            const jsonStr = line.slice(5).trim()
            if (!jsonStr) continue

            try {
              const data = JSON.parse(jsonStr)

              if (data.content) {
                currentContent += data.content
                setMessages(prev => {
                  const updated = [...prev]
                  updated[updated.length - 1] = {
                    role: 'assistant',
                    content: currentContent,
                    timestamp: new Date().toISOString(),
                    rag_sources: currentSources
                  }
                  return updated
                })
              }

              if (data.sources) {
                currentSources = data.sources
              }

              if (data.chat_id) {
                newChatId = data.chat_id
                if (!activeChat) {
                  setActiveChat(data.chat_id)
                }
              }
            } catch (e) {
            }
          }
        }
      }

      if (currentSources) {
        setMessages(prev => {
          const updated = [...prev]
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            rag_sources: currentSources
          }
          return updated
        })
      }

    } catch (err) {
      console.error('Failed to send message:', err)
      setLoading(false)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, something went wrong. Please try again.',
        timestamp: new Date().toISOString()
      }])
    }

    fetchChats()
  }

  return (
    <div className="app">
      <ChatSidebar
        chats={chats}
        activeChat={activeChat}
        onSelectChat={loadChat}
        onNewChat={createNewChat}
        onDeleteChat={deleteChat}
      />
      <ChatWindow
        messages={messages}
        onSendMessage={sendMessage}
        loading={loading}
      />
    </div>
  )
}

export default App
