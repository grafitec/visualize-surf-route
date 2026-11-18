# Visualizing surf route 
Visualizing surf route is a personal data management project and a Python-based tool for transforming GPS activity data into animated route visualizations and video sequences. The project takes GPS data from TCX files, processes the activity information, and generates frame-by-frame animations using Matplotlib. The resulting frames can be exported as PNG images and assembled into a video using FFmpeg or further edited in a video editor.
The project is designed as a practical learning platform for learning python, plotly, data analysis, software development and n8n for automation. Visualizing my surf rides and emails me a videos and pictures ready to upload on social media. 

 
## Features
- Scans gmail for importing the data
- TCX data processing – Extracts GPS coordinates and timestamps from TCX files.
- GPS route visualization – Converts geographic coordinates into a projected coordinate system for accurate map rendering.
- Route animation – Animates the GPS track point by point.
- Custom map rendering – Generates map backgrounds using OSMnx and OpenStreetMap data.
- Transparent and solid backgrounds – Supports transparent PNG exports as well as black-background compositions.
- Video-ready output – Exports individual frames that can be assembled into videos using FFmpeg or a video editor.
- Custom graphical overlays – Supports transparent PNG graphics and additional visual elements.
- Sends a email with the files
