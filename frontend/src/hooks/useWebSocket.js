import { useState, useEffect, useRef } from 'react';

export function useWebSocket(url) {
  const [ws, setWs] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const reconnectTimeout = useRef(null);

  useEffect(() => {
    let socket = null;
    
    const connect = () => {
      try {
        socket = new WebSocket(url);
        
        socket.onopen = () => {
          console.log('🔌 WebSocket connected');
          setIsConnected(true);
        };
        
        socket.onclose = () => {
          console.log('🔌 WebSocket disconnected');
          setIsConnected(false);
          
          // Attempt reconnect after 3 seconds
          if (reconnectTimeout.current) {
            clearTimeout(reconnectTimeout.current);
          }
          reconnectTimeout.current = setTimeout(connect, 3000);
        };
        
        socket.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
        
        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            setLastMessage(data);
          } catch (e) {
            console.error('Failed to parse WebSocket message:', e);
          }
        };
        
        setWs(socket);
      } catch (error) {
        console.error('WebSocket connection failed:', error);
        // Retry connection
        if (reconnectTimeout.current) {
          clearTimeout(reconnectTimeout.current);
        }
        reconnectTimeout.current = setTimeout(connect, 3000);
      }
    };
    
    connect();
    
    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, [url]);

  const sendMessage = (data) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(typeof data === 'string' ? data : JSON.stringify(data));
      return true;
    }
    return false;
  };

  return { ws, isConnected, lastMessage, sendMessage };
}