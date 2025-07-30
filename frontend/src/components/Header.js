import Link from 'next/link';

export default function Header() {

  return (
    <header className="bg-gray-900 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
        <Link href="/">
          <span className="text-xl font-bold cursor-pointer">My Media</span>
        </Link>

        <nav className="space-x-4">
          <Link href="/home" className="hover:underline">Home</Link>
          <Link href="/upload" className="hover:underline">Upload</Link>
          <Link href="/profile" className="hover:underline">Profile</Link>
          <Link href="/logout" className="hover:underline text-red-400">Logout</Link>
        </nav>
      </div>
    </header>
  )
};
