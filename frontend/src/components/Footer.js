import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-white py-6 mt-10">
      <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row justify-center items-center gap-4">
        <p className="text-sm text-gray-400">&copy; {new Date().getFullYear()} VidShare. All rights reserved.</p>
      </div>
    </footer>
  );
}
