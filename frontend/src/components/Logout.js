'use client';

import Cookies from 'js-cookie';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';

export default function LogoutButton() {
  const router = useRouter();
  const { refreshAuth } = useAuth();

  const handleLogout = () => {
    Cookies.remove('AuthToken');
    refreshAuth();
    router.push('/home'); // or wherever you want to redirect after logout
  };

  return (
    <button
      onClick={handleLogout}
      className="hover:underline"
    >
      Logout
    </button>
  );
}
