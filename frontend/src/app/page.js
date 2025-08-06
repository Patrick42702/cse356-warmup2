'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-950 text-white flex items-center justify-center px-4">
      <div className="max-w-4xl text-center space-y-6 py-20">
        <h1 className="text-4xl md:text-6xl font-extrabold text-yellow-100">
          Welcome to <span className="text-red-500">VidShare</span>
        </h1>

        <p className="text-gray-300 text-lg md:text-xl">
          Upload, stream, and share videos seamlessly. VidShare brings you the fastest way to share your story with the world.
        </p>

        <div className="flex justify-center space-x-4">
          <Link
            href="/signup"
            className="bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-6 rounded-lg transition"
          >
            Get Started
          </Link>
          <Link
            href="/upload"
            className="bg-white text-red-700 font-semibold py-2 px-6 rounded-lg hover:bg-gray-100 transition"
          >
            Upload a Video
          </Link>
        </div>

        {/* Optional: Add a hero image or illustration */}
        <div className="mt-10">
          <img
            src="/video-illustration.svg" // Replace with a real asset or remove
            alt="Video sharing illustration"
            className="w-full max-w-md mx-auto opacity-80"
          />
        </div>
      </div>
    </main>
  );
}
