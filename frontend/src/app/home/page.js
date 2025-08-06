'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';
import Image from 'next/image';
import Link from 'next/link';

export default function ExampleComponent() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const payload = {
      "size": 10,
    }
    const req = axios.post(`/api/video/videos`,
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
      {data.data.videos.length === 0 && "There are no videos currently uploaded. Upload something to view!"}
      {(data.data.videos.length > 0) && (data.data.videos.map((video, index) => (
        <div key={index} className="border rounded p-4 shadow">
          {video.thumbnail_url && (
            <Link href={`/player/${video.video_id}`} className="block">
              <Image
                src={video.thumbnail_url}
                alt={video.title || `Thumbnail for video ${index + 1}`}
                width={300}
                height={200}
                className="mt-2 rounded height-auto w-auto"
              />
            </Link>
          )}
          <p>Title: {video.title}</p>
          <p>User: {video.user}</p>
        </div>
      )))}
    </div>
  );

}
