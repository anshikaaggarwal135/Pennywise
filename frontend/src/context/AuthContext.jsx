import { createContext, useContext, useState } from 'react';
import api from '../lib/api';
const AuthContext = createContext(null);
export function AuthProvider({ children }) {
 const [user,setUser] = useState(() => { try{return JSON.parse(localStorage.getItem('pennywise_user'))}catch{return null} });
 const save = data => { localStorage.setItem('pennywise_token',data.access_token); localStorage.setItem('pennywise_user',JSON.stringify(data.user)); setUser(data.user); };
 const login = async (email,password) => save((await api.post('/auth/login',{email,password})).data);
 const register = async (name,email,password) => save((await api.post('/auth/register',{name,email,password})).data);
 const logout = () => {localStorage.removeItem('pennywise_token');localStorage.removeItem('pennywise_user');setUser(null)};
 return <AuthContext.Provider value={{user,login,register,logout}}>{children}</AuthContext.Provider>
}
export const useAuth=()=>useContext(AuthContext);
