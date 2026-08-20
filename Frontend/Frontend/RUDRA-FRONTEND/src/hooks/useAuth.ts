import { useAuthContext } from '../context/AuthContext';
import type { AuthContextType } from '../types/auth';

export function useAuth(): AuthContextType {
  return useAuthContext();
}

export default useAuth;
