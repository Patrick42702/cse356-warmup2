'use client';

import Link from 'next/link';
import Logout from './Logout';
import { useAuth } from '@/context/AuthContext';

export default function Header() {
  const { isLoggedIn } = useAuth();

  return (
    <header className="bg-gray-900 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link href="/">
            <span className="text-yellow-100 text-xl font-bold cursor-pointer">VidShare</span>
          </Link>
          <nav className="space-x-4">
            <Link href="/home" className="">Home</Link>
            <Link href="/upload" className="">Upload</Link>
            <Link href="/profile" className="">Profile</Link>
          </nav>
        </div>
        {isLoggedIn ? (
          <Logout />
        ) : (
          <div className="flex items-center space-x-4">
            <Link href="/signup" className="">Sign up</Link>
            <Link href="/login" className="">Login</Link>
          </div>
        )}
      </div>
    </header>
  )
};

