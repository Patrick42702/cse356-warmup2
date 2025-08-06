'use client'

import { useEffect, useRef, useState } from 'react'
import { useParams } from 'next/navigation'

export default function DashPlayerPage() {
  const videoRef = useRef(null)
  const { video_id } = useParams()
  const [player, setPlayer] = useState(null)
  const [bitrates, setBitrates] = useState([])
  const mpdUrl = `/api/video/dash/${video_id}/${video_id}.mpd`

  useEffect(() => {
    if (!video_id) return

    import('dashjs').then(dashjs => {
      const p = dashjs.MediaPlayer().create();

      p.initialize(videoRef.current, mpdUrl, false);

      p.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, () => {
        const tracks = p.getTracksFor('video')
        const track = tracks[0];
        const availableBitrates = track.bitrateList.map((t, index) => ({
          // qualityIndex: index,
          height: t.height,
          bandwidth: t.bandwidth,
          width: t.width
        }))
        setBitrates(availableBitrates)
      })

      p.on(dashjs.MediaPlayer.events.ERROR, function(e) {
        if (e.error.code === dashjs.MediaPlayer.errors.BUFFER_APPEND_ERROR) {
          console.log('Buffer append error, attempting recovery...');
          p.reset();
          p.attachView(videoRef.current);
          p.attachSource(mpdUrl);
        }
      });

      setPlayer(p)
    })

    // Optional cleanup
    return () => {
      if (player) {
        player.reset()
      }
    }
  }, [video_id])

  const handleChangeResolution = (e) => {
    const qualityIndex = parseInt(e.target.value, 10)
    if (!player) return

    if (qualityIndex === -1) {
      player.updateSettings({ streaming: { abr: { autoSwitchBitrate: { video: true } } } });
    } else {
      player.updateSettings({ streaming: { abr: { autoSwitchBitrate: { video: false } } } })
      player.setRepresentationForTypeByIndex('video', qualityIndex, true)
    }
  }

  const handlePlaybackRateChange = (event) => {
    const rate = parseFloat(event.target.value);
    player.setPlaybackRate(rate);
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">Video Player</h1>
      {/*TODO:  CHANGE VIDEO_ID TO A VIDEO TITLE*/}

      <video
        ref={videoRef}
        controls
        style={{ width: '100%', maxWidth: '800px' }}
      />

      {bitrates.length > 0 && (
        <div className="mt-4">
          <label className="mr-2">Select Resolution:</label>
          <select onChange={handleChangeResolution} className="p-1 border rounded">
            <option value="-1">Auto</option>
            {bitrates.map((br, i) => (
              <option key={i} value={i}>
                {br.height}p ({Math.round(br.bandwidth) / 1000} kbps)
              </option>
            ))}
          </select>
        </div>
      )}
      <select
        id="playbackRate"
        onChange={handlePlaybackRateChange}
        defaultValue="1"
        className="border rounded px-2 py-1"
      >
        <option value="0.5">0.5x</option>
        <option value="0.75">0.75x</option>
        <option value="1">1x</option>
        <option value="1.25">1.25x</option>
        <option value="1.5">1.5x</option>
        <option value="2">2x</option>
      </select>
    </div>
  )
}

