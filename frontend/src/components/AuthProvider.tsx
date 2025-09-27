import { createContext, useContext, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  tenant_name: string;
  role: 'owner' | 'manager' | 'clerk';
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  isLoading: false,
});

// Mock user for development
const mockUser: User = {
  id: '1',
  email: 'demo@example.com',
  first_name: 'Demo',
  last_name: 'User',
  full_name: 'Demo User',
  tenant_name: 'Demo Company',
  role: 'owner',
};

export function AuthProvider({ children }: { children: ReactNode }) {
  // For development, we'll simulate being authenticated
  const isAuthenticated = true;
  const user = mockUser;
  const isLoading = false;

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}