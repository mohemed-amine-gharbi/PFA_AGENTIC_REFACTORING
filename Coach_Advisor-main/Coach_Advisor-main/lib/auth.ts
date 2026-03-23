// lib/auth.ts
export interface User {
  id: string;
  email: string;
  name?: string;
}

// Stockage local simulé
const STORAGE_KEY = 'auth_users';
const CURRENT_USER_KEY = 'current_user';

// Récupérer tous les utilisateurs
const getUsers = (): Record<string, { password: string; user: User }> => {
  if (typeof window === 'undefined') return {};
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored ? JSON.parse(stored) : {};
};

// Sauvegarder les utilisateurs
const saveUsers = (users: Record<string, { password: string; user: User }>) => {
  if (typeof window === 'undefined') return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(users));
};

// Inscription
export const signUp = async (email: string, password: string, name?: string): Promise<User> => {
  const users = getUsers();
  
  if (users[email]) {
    throw new Error('Cet email est déjà utilisé');
  }
  
  const newUser: User = {
    id: crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2) + Date.now().toString(36),
    email,
    name,
  };
  
  users[email] = {
    password,
    user: newUser,
  };
  
  saveUsers(users);
  
  // Connecter automatiquement après inscription
  localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(newUser));
  
  return newUser;
};

// Connexion
export const signIn = async (email: string, password: string): Promise<User> => {
  const users = getUsers();
  const userRecord = users[email];
  
  if (!userRecord || userRecord.password !== password) {
    throw new Error('Email ou mot de passe incorrect');
  }
  
  localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(userRecord.user));
  
  return userRecord.user;
};

// Déconnexion
export const signOut = async (): Promise<void> => {
  localStorage.removeItem(CURRENT_USER_KEY);
};

// Récupérer l'utilisateur courant
export const getCurrentUser = (): User | null => {
  if (typeof window === 'undefined') return null;
  const user = localStorage.getItem(CURRENT_USER_KEY);
  return user ? JSON.parse(user) : null;
};

// Vérifier si l'utilisateur est authentifié
export const isAuthenticated = (): boolean => {
  return getCurrentUser() !== null;
};