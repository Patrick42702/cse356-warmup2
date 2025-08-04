import Link from 'next/link';
import Logout from './Logout';

export default function Header() {

  return (
    <header className="bg-gray-900 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 py-3 flex-auto">
        <Link href="/">
          <span className="text-red-700 text-xl font-bold cursor-pointer">My Media</span>
        </Link>
        <nav className="space-x-4">
          <Link href="/home" className="text-red-700 hover:underline">Home</Link>
          <Link href="/signup" className="hover:underline">Sign up</Link>
          <Link href="/login" className="hover:underline">Login</Link>
          <Link href="/upload" className="hover:underline">Upload</Link>
          <Link href="/profile" className="hover:underline">Profile</Link>
          <Logout />
        </nav>
      </div>
    </header>
  )
};
