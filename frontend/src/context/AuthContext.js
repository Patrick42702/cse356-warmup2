'use client';

import { createContext, useContext, useEffect, useState } from 'react';

const AuthContext = createContext({
  isLoggedIn: false,
  refreshAuth: () => { },
});

export function AuthProvider({ children }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const refreshAuth = () => {
    const loggedIn = document.cookie
      .split('; ')
      .some(cookie => cookie.startsWith('AuthToken='));
    setIsLoggedIn(loggedIn);
  };

  useEffect(() => {
    refreshAuth();
  }, []);

  return (
    <AuthContext.Provider value={{ isLoggedIn, refreshAuth }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
