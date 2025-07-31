import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-white py-6 mt-10">
      <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center gap-4">
        <p className="text-sm text-gray-400">&copy; {new Date().getFullYear()} My Media. All rights reserved.</p>

        <nav className="flex space-x-6">
          <Link href="/" className="hover:text-gray-200 transition">Home</Link>
          <Link href="/upload" className="hover:text-gray-200 transition">Upload</Link>
          <Link href="/profile" className="hover:text-gray-200 transition">Profile</Link>
          <Link href="/about" className="hover:text-gray-200 transition">About</Link>
        </nav>
      </div>
    </footer>
  );
}
