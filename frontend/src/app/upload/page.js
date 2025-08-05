'use client';
import axios from 'axios';
import Cookies from 'js-cookie';

import { useState } from 'react';

const ALLOWED_FILE_TYPES = ['video/mp4', 'video/quicktime'];

export default function UploadForm() {
  const [status, setStatus] = useState({
    'message': '',
    'type': ''
  })
  const [form, setForm] = useState({
    'title': '',
    'file': null
  });

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected && ALLOWED_FILE_TYPES.includes(selected.type)) {
      setForm({
        'title': form.title,
        'file': selected
      });
    }
    else {
      setStatus({
        'message': 'Please select a valid MP4 or MOV file.',
        'type': 'error'
      });
      setForm({
        'title': form.title,
        'file': null
      });
    }
  };


  const handleSubmit = async (e) => {
    e.preventDefault();
    const title = e.target.title.value.trim();
    if (!form.file) {
      setStatus({
        'message': 'Please select a file to upload.',
        'type': 'error'
      });
      return;
    }
    if (title === '') {
      setStatus({
        'message': 'Please enter a title for the video.',
        'type': 'error'
      });
      return;
    }

    const formData = new FormData();
    formData.append('video', form.file);
    formData.append('title', title);

    try {
      const token = Cookies.get('AuthToken');
      if (!token) {
        setStatus({
          'message': 'You must be logged in to upload a video.',
          'type': 'error'
        });
        return;
      }

      const res = await axios.post(
        `/api/video/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': token || '',
          },
        });
      if (res.status === 200) {
        setStatus({
          'message': 'Video uploaded successfully!',
          'type': 'success'
        });
        setForm({
          'title': '',
          'file': null
        });
      }
    } catch (err) {
      if (err.response) {
        // Backend responded with a non-2xx status code
        setStatus({
          'message': `Upload failed: ${err.response.data.error || 'Unknown error'}`,
          'type': 'error'
        });
      } else if (err.request) {
        // Request was made but no response received
        setStatus({
          'message': 'No response from server. Please try again later.',
          'type': 'error'
        });
      } else {
        // Other errors
        setStatus({
          'message': `An error occurred: ${err.message}`,
          'type': 'error'
        });
      }
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
      <input
        type="text"
        name="title"
        placeholder="Video Title"
        className="block w-full text-sm border rounded p-2"
      />
      <button
        type="submit"
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Upload MP4
      </button>
      {status.message && (
        <p className={`text-sm ${(status.type === 'error') ? 'text-red-600' : 'text-green-600'}`}>
          {status.message}
        </p>
      )}
    </form>
  );
}
