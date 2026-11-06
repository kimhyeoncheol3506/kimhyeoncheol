# Encode the rendered PNG sequence + soundtrack into a Twitter-ready MP4 (H.264 High, 1080p30, AAC).
# usage: powershell -File tools\encode.ps1 [-Frames out\frames] [-Ext png|jpg] [-Out out\halo_1080p30.mp4] [-Crf 16] [-Audio x.wav]
param([string]$Frames = 'out\frames', [string]$Ext = 'png', [string]$Out = 'out\halo_1080p30.mp4', [int]$Crf = 16, [string]$Audio = 'out\music\soundtrack.wav')
ffmpeg -y -hide_banner -framerate 30 -i "$Frames\f_%05d.$Ext" -i $Audio `
  -c:v libx264 -preset slow -crf $Crf -profile:v high -level 4.2 -pix_fmt yuv420p `
  -x264-params "keyint=60:min-keyint=30:aq-mode=3:deblock=-1,-1:colorprim=bt709:transfer=bt709:colormatrix=bt709" -maxrate 30M -bufsize 60M `
  -vf "scale=out_color_matrix=bt709:out_range=tv:flags=lanczos+accurate_rnd+full_chroma_int,format=yuv420p" -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv `
  -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart $Out
Get-Item $Out | Select-Object Name, @{n = 'MB'; e = { [math]::Round($_.Length / 1MB, 1) } }
