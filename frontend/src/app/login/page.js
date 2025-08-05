'use client';
import React from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation';

export default function SignUpPage() {

  const router = useRouter();
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
      email: formData.get('email'),
      password: formData.get('password'),
    };
    const auth = `/api/auth/login`;
    const res = await axios.post(auth, data)
      .then(async response => {
        if (response.status === 200) {
          Cookies.set('AuthToken', `Bearer ${response.data.data.token}`, {
            expires: 7
          });
          router.push("/home");
        }
      })
      .catch(err => {
        if (err.response) {
          const errorMsg = err.response.data.error;
          setMessage(`Login failed: ${errorMsg}`);
        } else if (err.request) {
          // Request was made but no response received
          setMessage('No response from server.');
        } else {
          // Other errors
          setMessage('An error occurred while uploading.');
        };
      });
  }

  return (
    <div>
      <h1 className="text-2xl mb-4"></h1>
      <form onSubmit={handleSubmit} className="max-w-md mx-auto">
        <div className="mb-4">
          <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email</label>
          <input type="email" id="email" name="email" required className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm" />
        </div>
        <div className="mb-4">
          <label htmlFor="password" className="block text-sm font-medium text-gray-700">Password</label>
          <input type="password" id="password" name="password" required className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm" />
          {message && <p className="text-red-700">{message}</p>}
        </div>
        <button type="submit" className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">Login</button>
      </form>
    </div>
  )
}

