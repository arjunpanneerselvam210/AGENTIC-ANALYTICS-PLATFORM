import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ChatProvider } from './context/ChatContext';
import { AppRouter } from './router/AppRouter';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ChatProvider>
          <AppRouter />
        </ChatProvider>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
