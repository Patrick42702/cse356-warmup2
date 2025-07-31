'use client';
import axios from 'axios';

import { useState } from 'react';

const ALLOWED_FILE_TYPES = ['video/mp4', 'video/quicktime'];

export default function UploadForm() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected && ALLOWED_FILE_TYPES.includes(selected.type)) {
      setFile(selected);
      setMessage('');
    } else {
      setFile(null);
      setMessage('Only MP4 files are allowed.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage('Please select an MP4 file to upload.');
      return;
    }

    const formData = new FormData();
    formData.append('video', file);

    try {
      const res = await axios.post(
        `${process.env.NEXT_PUBLIC_VIDEO_API_URL}/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

      if (res.ok) {
        setMessage('File uploaded successfully.');
        setFile(null);
      } else {
        const err = await res.text();
        setMessage(`Upload failed: ${err}`);
      }
    } catch (err) {
      setMessage('An error occurred while uploading.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 border rounded max-w-md mx-auto mt-10">
      <input
        type="file"
        accept="video/*"
        onChange={handleFileChange}
        className="block w-full text-sm"
      />
      <button
        type="submit"
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Upload MP4
      </button>
      {message && <p className="text-sm text-red-600">{message}</p>}
    </form>
  );
}

