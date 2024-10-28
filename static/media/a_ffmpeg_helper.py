import os
import subprocess

# Configuration
input_dir = 'videos'
output_base = 'output'

# Video filter for padding to 16:9 aspect ratio
scale_filter = "scale='if(gt(a,16/9),1280,-2)':'if(gt(a,16/9),-2,720)',pad=1280:720:(ow-iw)/2:(oh-ih)/2:black"

# FFmpeg resolution and bitrate options
ffmpeg_options = [
    ('254k', '320x180'),
    ('507k', '320x180'),
    ('759k', '480x270'),
    ('1013k', '640x360'),
    ('1254k', '640x360'),
    ('1883k', '768x432'),
    ('3134k', '1024x576'),
    ('4952k', '1280x720')
]

# DASH options
dash_options = [
    '-use_template', '1',
    '-use_timeline', '1',
    '-seg_duration', '10',
    '-adaptation_sets', 'id=0,streams=v',
    '-f', 'dash'
]

# Process each video file in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith('.mp4'):
        # Extract video ID
        video_id = filename.split('-')[0]

        # Build FFmpeg command for DASH
        input_path = os.path.join(input_dir, filename)
        output_mpd = f"{video_id}.mpd"

        # Start constructing the FFmpeg command
        ffmpeg_cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-vf', scale_filter, '-report'
        ]

        # Add video bitrates and resolutions
        for i, (bitrate, resolution) in enumerate(ffmpeg_options):
            ffmpeg_cmd.extend([
                '-map', '0:v',
                f'-b:v:{i}', bitrate,
                f'-s:v:{i}', resolution
            ])

        # Set segment names with video_id
        ffmpeg_cmd.extend([
            '-init_seg_name', f"init_{video_id}_$RepresentationID$.mp4",
            '-media_seg_name', f"chunk_{video_id}_$Bandwidth$_$Number$.m4s"
        ])

        # Add DASH options and output MPD file path
        ffmpeg_cmd.extend(dash_options)
        ffmpeg_cmd.append(output_mpd)

        # Run the FFmpeg command for DASH
        print(f"Processing {filename} with video ID {video_id}")
        subprocess.run(ffmpeg_cmd)

        # Generate thumbnail
        thumbnail_path = f"thumbnail_{video_id}.jpg"
        thumbnail_cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-vf', scale_filter, '-vframes', '1', thumbnail_path
        ]
        print(f"Generating thumbnail for {filename} with video ID {video_id}")
        subprocess.run(thumbnail_cmd)

print("Processing complete.")
