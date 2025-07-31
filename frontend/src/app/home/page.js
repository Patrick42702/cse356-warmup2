'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';
import Image from 'next/image';

export default function ExampleComponent() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log(`${process.env.NEXT_PUBLIC_VIDEO_API_URL}/api/video/videos`); // Log the URL to check if it's correct
    const payload = {
      "size": 10,
    }
    const req = axios.post(`${process.env.NEXT_PUBLIC_VIDEO_API_URL}/api/video/videos`,
      JSON.stringify(payload),
      {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      })
      .then(response => setData(response.data))
      .catch(error => {
        console.error('Error fetching data:', error)
        setError(error);
      });
  }, []);

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  if (!data) {
    return <div>Loading...</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {data.data.videos.map((video, index) => (
        <div key={index} className="border rounded p-4 shadow">
          <p>{video.description || 'No description available.'}</p>
          {/* Add a thumbnail or link if available */}
          {video.thumbnail_url && (
            <Image
              src={video.thumbnail_url}
              alt={video.title || `Thumbnail for video ${index + 1}`}
              width={300}
              height={200}
              className="mt-2 rounded"
            />
          )}
        </div>
      ))}
    </div>
  );

}
