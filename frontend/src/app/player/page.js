'use client'

import { useEffect, useRef, useState } from 'react'

export default function DashPlayerPage() {
  const videoRef = useRef(null)
  const [player, setPlayer] = useState(null)
  const [bitrates, setBitrates] = useState([])

  useEffect(() => {
    import('dashjs').then(dashjs => {
      const p = dashjs.MediaPlayer().create()
      p.initialize(
        videoRef.current,
        'http://localhost/api/video/dash/f60e2a68-b283-4ac8-99aa-cf739027b066/f60e2a68-b283-4ac8-99aa-cf739027b066.mpd',
        true
      )
      p.updateSettings({ streaming: { abr: { autoSwitchBitrate: { video: false } } } })

      p.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, () => {
        const availableBitrates = p.getTracksFor('video')
        setBitrates(availableBitrates)
      })

      setPlayer(p)
    })
  }, [])

  const handleChangeResolution = (e) => {
    const index = parseInt(e.target.value, 10)
    if (player) {
      player.setQualityFor('video', index)
    }
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">MPEG-DASH Player with Resolution Selector</h1>

      <video
        ref={videoRef}
        controls
        style={{ width: '100%', maxWidth: '800px' }}
      />

      <div className="mt-4">
        <label className="mr-2">Select Resolution:</label>
        <select onChange={handleChangeResolution} className="p-1 border rounded">
          {bitrates.map((br, i) => (
            <option key={i} value={i}>
              {br.height}p ({Math.round(br.bitrate / 1000)} kbps)
            </option>
          ))}
        </select>
      </div>
    </div>
  )
}

