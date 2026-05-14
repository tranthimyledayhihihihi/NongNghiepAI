import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { authApi } from '../services/authApi';

const AUTH_TOKEN_KEY = 'token';
const AUTH_USER_KEY = 'agriai_user';

const AuthContext = createContext(null);

const normalizeUser = (user) => ({
  id: user.user_id ?? user.id,
  name: user.full_name ?? user.name,
  email: user.email,
  phone: user.phone_number ?? user.phone,
  zaloId: user.zalo_id ?? user.zaloId,
  role: user.role,
  region: user.region,
});

const readStoredUser = () => {
  try {
    const rawUser = localStorage.getItem(AUTH_USER_KEY);
    return rawUser ? JSON.parse(rawUser) : null;
  } catch {
    localStorage.removeItem(AUTH_USER_KEY);
    return null;
  }
};

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem(AUTH_TOKEN_KEY));
  const [user, setUser] = useState(readStoredUser);
  const [loading, setLoading] = useState(Boolean(localStorage.getItem(AUTH_TOKEN_KEY)));

  const persistSession = ({ access_token: accessToken, user: nextUser }) => {
    const normalizedUser = normalizeUser(nextUser);
    localStorage.setItem(AUTH_TOKEN_KEY, accessToken);
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(normalizedUser));
    setToken(accessToken);
    setUser(normalizedUser);
    return normalizedUser;
  };

  const clearSession = () => {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
    setToken(null);
    setUser(null);
  };

  useEffect(() => {
    let cancelled = false;

    const hydrateUser = async () => {
      const storedToken = localStorage.getItem(AUTH_TOKEN_KEY);
      if (!storedToken) {
        setLoading(false);
        return;
      }

      try {
        const currentUser = await authApi.me();
        if (!cancelled) {
          const normalizedUser = normalizeUser(currentUser);
          localStorage.setItem(AUTH_USER_KEY, JSON.stringify(normalizedUser));
          setUser(normalizedUser);
          setToken(storedToken);
        }
      } catch {
        if (!cancelled) {
          clearSession();
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    hydrateUser();

    return () => {
      cancelled = true;
    };
  }, []);

  const login = async ({ email, password }) => {
    const response = await authApi.login({ email, password });
    return persistSession(response);
  };

  const register = async ({ fullName, email, password, phoneNumber, zaloId, region }) => {
    const response = await authApi.register({ fullName, email, password, phoneNumber, zaloId, region });
    return persistSession(response);
  };

  const logout = () => {
    clearSession();
  };

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      isAuthenticated: Boolean(token),
      login,
      register,
      logout,
    }),
    [token, user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }

  return context;
};
