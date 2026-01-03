import React, { useState, useRef, useEffect } from 'react';
import clsx from 'clsx';
import styles from './Chatbot.module.css';

// Define the Chatbot component
const Chatbot = ({ title = "Book Assistant", subtitle = "Ask me anything about humanoid robotics and AI" }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your book assistant. Ask me anything about humanoid robotics and AI!",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Function to handle sending messages
  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!inputValue.trim() || isLoading) return;

    // Add user message to the chat
    const userMessage = {
      id: Date.now(),
      text: inputValue.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      // Send the query to the backend API
      const response = await fetch('http://localhost:8000/api/v1/rag-agent/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query_text: inputValue.trim()
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Add bot response to the chat
      const botMessage = {
        id: Date.now() + 1,
        text: data.content,
        sender: 'bot',
        timestamp: new Date(),
        sources: data.retrieved_chunks,
        confidence: data.confidence_score
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error('Error sending message:', err);
      setError(err.message);

      // Add error message to the chat
      const errorMessage = {
        id: Date.now() + 1,
        text: `Sorry, I encountered an error: ${err.message}. Please try again.`,
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Function to clear chat
  const handleClearChat = () => {
    setMessages([
      {
        id: 1,
        text: "Hello! I'm your book assistant. Ask me anything about humanoid robotics and AI!",
        sender: 'bot',
        timestamp: new Date()
      }
    ]);
    setError(null);
  };

  return (
    <div className={clsx('container', styles.chatbotContainer)}>
      <div className={styles.chatbotHeader}>
        <h3>{title}</h3>
        <p>{subtitle}</p>
      </div>

      <div className={styles.chatbotWrapper}>
        <div className={styles.messagesContainer}>
          {messages.map((message) => (
            <div
              key={message.id}
              className={clsx(
                styles.message,
                message.sender === 'user' ? styles.userMessage : styles.botMessage
              )}
            >
              <div className={styles.messageContent}>
                <div className={styles.messageText}>{message.text}</div>
                {message.sources && message.sources.length > 0 && (
                  <details className={styles.sourcesDetails}>
                    <summary>Sources ({message.sources.length})</summary>
                    <div className={styles.sourcesList}>
                      {message.sources.slice(0, 2).map((source, index) => (
                        <div key={index} className={styles.sourceItem}>
                          <small className={styles.sourceContent}>
                            {source.content.substring(0, 100)}...
                          </small>
                          <small className={styles.similarityScore}>
                            Similarity: {(source.similarity_score * 100).toFixed(1)}%
                          </small>
                        </div>
                      ))}
                    </div>
                  </details>
                )}
                {message.confidence !== undefined && (
                  <small className={styles.confidenceScore}>
                    Confidence: {(message.confidence * 100).toFixed(1)}%
                  </small>
                )}
              </div>
              <div className={styles.messageTimestamp}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className={clsx(styles.message, styles.botMessage)}>
              <div className={styles.messageContent}>
                <div className={styles.typingIndicator}>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {error && (
          <div className={styles.errorBanner}>
            <strong>Error:</strong> {error}
          </div>
        )}

        <form onSubmit={handleSendMessage} className={styles.inputForm}>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask a question about the book content..."
            disabled={isLoading}
            className={styles.messageInput}
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className={clsx(styles.sendButton, {
              [styles.loadingButton]: isLoading
            })}
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </form>

        <div className={styles.chatActions}>
          <button onClick={handleClearChat} className={styles.clearButton}>
            Clear Chat
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;