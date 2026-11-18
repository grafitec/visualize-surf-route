
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

## Example Output
<img width="720" height="1280" alt="rutt_cityLines (2)" src="https://github.com/user-attachments/assets/e7e08473-1712-4ed4-b4f6-56ab2a3b741c" />
<img width="720" height="1280" alt="rutt_map (1)" src="https://github.com/user-attachments/assets/00c3f56c-e80e-420f-bddf-c878c532db03" />


## Technologies
- Python
- Pandas – Data processing
- NumPy – Numerical calculations
- Matplotlib – Visualization and animation
- PyProj – Geographic coordinate transformations
- OSMnx – Custom map generation
- Pillow – Image processing
- FFmpeg – Video encoding
- Gmail - Read and send mails
- n8n - automation

## How It Works
The project follows a processing pipeline:

- Track your surfride
- Send the TCX file to gmail with settings
- n8n automation trigger an action to run the code with flask server
- Import GPS data – Load activity data from a TCX file.
- Extract information – Parse timestamps, latitude, longitude and available activity metrics.
- Process coordinates – Transform GPS coordinates from WGS84 (EPSG:4326) to Web Mercator (EPSG:3857).
- Calculate activity metrics – Calculate route distance, elapsed time and speed.
- Generate visualization – Render the route, markers, activity information and optional map background.
- Export frames – Save each animation frame as an individual PNG image.
- Create video – Combine the exported frames into a video using FFmpeg or an external video editor.
- Email the outputfiles ready to post on social media

## Installation

Clone the repository:

git clone https://github.com/grafitec/visualize-surf-route.git
cd visualize-surf-route

Install the required dependencies:
pip install -r requirements.txt

Make sure FFmpeg is installed and available in your system PATH if you want to generate videos directly.

## Project Goals
This project was developed to explore how GPS activity data can be transformed into visually engaging animations.
It combines data processing, geographic coordinate transformations, mathematical calculations and graphical rendering into a reusable Python workflow.
I wanted to learn and explore more python challenges and make a useful tool to my day to day surfing rides.
