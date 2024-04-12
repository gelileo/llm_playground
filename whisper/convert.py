import ffmpeg

infile = "user_instr.m4a"
outfile = "user_instrls .mp3"

# You can adjust the bitrate variable to your desired setting, like "128k", "192k", "256k", or "320k" for different levels of quality and file size.
bitrate = "64k"  # Good for mono spoken audio
ffmpeg.input(infile).output(outfile, audio_bitrate=bitrate).run()
