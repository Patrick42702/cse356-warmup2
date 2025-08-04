'use client';

import Cookies from 'js-cookie';
import { useRouter } from 'next/navigation';

export default function LogoutButton() {
  const router = useRouter();

  const handleLogout = () => {
    Cookies.remove('AuthToken');
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
