import json
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import os
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
import contextily as ctx
import subprocess
from pathlib import Path
from pyproj import Transformer
import osmnx as ox
import subprocess
from PIL import Image
import traceback

def read_gps_file(jsonFile):

    # Läs in GPS-data
    with open(jsonFile, encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # Gör om tiden till ett datum/tidsformat
    df["time"] = pd.to_datetime(df["time"])
    return df

def tcx_to_json(tcx_path, rideId=''):
    try:
        TCX_NS = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
        NS = {"tcx": TCX_NS}
        tcx_file = Path(tcx_path)
        if os.path.exists(tcx_file):
            root = ET.parse(tcx_file).getroot()

            max_speeds = []
            for lap in root.findall(".//tcx:Lap", NS):
                max_speed_el = lap.find("tcx:MaximumSpeed", NS)
                if max_speed_el is not None:
                    max_speeds.append(float(max_speed_el.text))
            if max_speeds:
                max_speed = max(max_speeds)
            points = []
            index = 0
            for point in root.findall(".//tcx:Trackpoint", NS):
                time_el = point.find("tcx:Time", NS)
                lat_el = point.find("tcx:Position/tcx:LatitudeDegrees", NS)
                lon_el = point.find("tcx:Position/tcx:LongitudeDegrees", NS)

                if time_el is None or time_el.text is None:
                    continue
                if lat_el is None or lon_el is None:
                    continue

                points.append({
                    "id": float(1),
                    "index": int(index),
                    "time": time_el.text,
                    "latitude": float(lat_el.text),
                    "longitude": float(lon_el.text),
                    "max_speed": float(max_speed),

                })
                index = index + 1

            if rideId == '':
                untrackedVersion = str(tcx_path).split('.')[0].split('_')[-1]
                json_filename = f"appleWatchRideData_rideId_{untrackedVersion}.json"
            else:
                json_filename = f"appleWatchRideData_rideId_{rideId}.json"
            json_folder = (
                    Path(__file__).parent.parent
                    / "data"
                    / "json"
            )
            json_folder.mkdir(parents=True, exist_ok=True)
            json_path = (Path(json_folder) / json_filename)
            json_file = Path(json_path)
            with json_file.open("w", encoding="utf-8") as f:
                json.dump(points, f, indent=2, ensure_ascii=False)
            path = str(json_file).replace('\\', '/')
            print('Done converting to json ' + path)
            return path
        else:
            return None
    except Exception:
        traceback.print_exc()

def visualize(df):
    fig = px.scatter_map()
    # Rita rutten på en karta
    fig = px.scatter_map(
        df,
        lat=df['latitude'],
        lon=df['longitude'],
        hover_name=df['time'],
        zoom=14,
        height=800,
        width=800,
        title="Min GPS-rutt"
    )

    # Lägg till linjer mellan GPS-punkterna
    fig.update_traces(
        mode="lines+markers",
        marker=dict(size=5)
    )

    fig.update_layout(
        map_style="open-street-map",
        map_center={
            "lat": df["latitude"].mean(),
            "lon": df["longitude"].mean()
        }
    )

    fig.show()

def preview_frame(df):
    df["time"] = pd.to_datetime(df["time"], utc=True)
    df = df.sort_values("time").reset_index(drop=True)

    # Haversine: avstånd mellan två GPS-punkter
    lat = np.radians(df["latitude"].to_numpy())
    lon = np.radians(df["longitude"].to_numpy())

    dlat = np.diff(lat)
    dlon = np.diff(lon)

    a = (
            np.sin(dlat / 2) ** 2
            + np.cos(lat[:-1]) * np.cos(lat[1:])
            * np.sin(dlon / 2) ** 2
    )

    distances = 2 * 6_371_000 * np.arcsin(
        np.sqrt(np.clip(a, 0, 1))
    )

    distance_km = distances.sum() / 1000
    duration = df["time"].iloc[-1] - df["time"].iloc[0]

    print(f"Distans: {distance_km:.2f} km")
    print(f"Tid: {duration}")

    # Rita rutten
    fig = go.Figure()

    fig.add_trace(go.Scattermap(
        lat=df["latitude"],
        lon=df["longitude"],
        mode="lines",
        line=dict(width=4, color="#FC5200"),
        name="Rutt"
    ))

    fig.update_layout(
        title=f"{distance_km:.2f} km · {duration}",
        map=dict(
            style="open-street-map",
            center=dict(
                lat=df["latitude"].mean(),
                lon=df["longitude"].mean()
            ),
            zoom=14
        ),
        height=700
    )

    fig.show()

def animated(df):

    # Antal bildrutor i animationen
    n_frames = 150

    # Välj jämnt fördelade punkter längs rutten
    frame_indices = np.unique(
        np.linspace(0, len(df) - 1, n_frames, dtype=int)
    )

    # Skapa kartan
    fig = go.Figure()

    # Rutten som växer
    fig.add_trace(go.Scattermap(
        lat=[df["latitude"].iloc[0]],
        lon=[df["longitude"].iloc[0]],
        mode="lines",
        line=dict(width=5, color="#FC5200"),
        name="Rutt"
    ))

    # Markör som visar aktuell position
    fig.add_trace(go.Scattermap(
        lat=[df["latitude"].iloc[0]],
        lon=[df["longitude"].iloc[0]],
        mode="markers",
        marker=dict(size=13, color="white"),
        name="Position"
    ))

    # Skapa animationens bildrutor
    frames = []

    for i in frame_indices:
        frames.append(
            go.Frame(
                data=[
                    go.Scattermap(
                        lat=df["latitude"].iloc[:i + 1],
                        lon=df["longitude"].iloc[:i + 1]
                    ),
                    go.Scattermap(
                        lat=[df["latitude"].iloc[i]],
                        lon=[df["longitude"].iloc[i]]
                    )
                ],
                traces=[0, 1],
                name=str(i)
            )
        )

    fig.frames = frames

    # Kartinställningar
    fig.update_layout(
        map=dict(
            style="open-street-map",
            center=dict(
                lat=df["latitude"].mean(),
                lon=df["longitude"].mean()
            ),
            zoom=13
        ),
        height=700,
        margin=dict(l=0, r=0, t=40, b=0),

        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[
                dict(
                    label="▶ Spela",
                    method="animate",
                    args=[
                        None,
                        dict(
                            frame=dict(duration=70, redraw=True),
                            transition=dict(duration=0),
                            fromcurrent=True,
                            mode="immediate"
                        )
                    ]
                ),
                dict(
                    label="⏸ Pausa",
                    method="animate",
                    args=[
                        [None],
                        dict(
                            frame=dict(duration=0, redraw=False),
                            mode="immediate"
                        )
                    ]
                )
            ]
        )]
    )

    fig.show()

class Crate_map_video():
    def __init__(self, df, mailData):

        # Inställningar
        self.FPS = 30
        self.N_FRAMES = 400
        self.WIDTH = 720
        self.HEIGHT = 1280
        self.ROUTE_COLOR = "#FC5200"
        self.mailData = mailData

        timestamps = pd.to_datetime(df["time"], utc=True)
        self.date = timestamps.iloc[0].strftime("%Y-%m-%d")

        # Konvertera GPS-koordinater till kartkoordinater
        transformer = Transformer.from_crs(
            "EPSG:4326", "EPSG:3857", always_xy=True
        )

        self.x, self.y = transformer.transform(
            df["longitude"].to_numpy(),
            df["latitude"].to_numpy()
        )

        self.count_distance(df)
        self.count_time(df)
        self.current_speed(df)
        self.max_speed_cal(df)

        # Välj bildrutor längs rutten
        self.indices = np.linspace(0, len(df) - 1, self.N_FRAMES).astype(int)

        self.bounds = self.calculate_bounds()

        # Rendera båda versionerna
        cityLines = []
        maps = []
        alpha = []
        filename_cityLines = self.render_frames(True, "frames_cityLines")
        cityLines.append(filename_cityLines)
        print('Done rendering cityLines')
        filename_map = self.render_frames(True, "frames_map")
        maps.append(filename_map)
        print('Done rendering map')
        filename_alpha = self.render_frames(False, "frames_alpha")
        alpha.append(filename_alpha)
        print('Done rendering with alpha')

        self.outputname_cityLines = filename_cityLines.split('frames_cityLines')[0]+'rutt_cityLines.mp4'
        cityLines.append(self.outputname_cityLines)
        self.outputname_alpha = filename_alpha.split('frames_alpha')[0]+'rutt_alpha.mp4'
        alpha.append(self.outputname_alpha)
        self.outputname_map = filename_map.split('frames_map')[0]+'rutt_map.mp4'
        maps.append(self.outputname_map)
        self.outputnames = [cityLines, alpha, maps]

        # MP4 export
        for outputname in self.outputnames:
            subprocess.run([
                "ffmpeg", "-y",
                "-framerate", str(self.FPS),
                "-i", outputname[0],
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-loglevel", "error",
                outputname[1]
            ], check=True)
            print('Done converting cityLines to mp4, ' + outputname[0])






    def render_frames(self, with_map, folder):

        fig, line, marker, distance_numbers, time_numbers= self.create_figure(with_map, folder)
        rootPath = Path(__file__).parent.parent
        frameFolder = (rootPath / 'export' / folder)
        Path(frameFolder).mkdir(parents=True, exist_ok=True)
        print('Starting exporting frames')
        for frame_number, i in enumerate(self.indices):
            line.set_data(self.x[:i+1], self.y[:i+1])
            marker.set_data([self.x[i]], [self.y[i]])

            filename = (f"{frameFolder}/frame_{frame_number:04d}.jpg")
            print(filename)
            fig.savefig(
                filename,
                dpi=100,
                facecolor="black",
                transparent=False,
                pad_inches=0
            )
        # Extra frames in the end
        for i, extraframes in enumerate(range(int(frame_number)+1, int(frame_number)+42)):
            filename = (f"{frameFolder}/frame_{str(extraframes).zfill(4)}.jpg")
            fig.savefig(
                filename,
                dpi=100,
                facecolor="black",
                transparent=False,
                pad_inches=0
            )

            filename = (f"{frameFolder}/frame_%04d.jpg")

        plt.close(fig)
        return filename


    def create_figure(self, with_map, folder):

        fig, ax = plt.subplots(
            figsize=(self.WIDTH / 100, self.HEIGHT / 100),
            dpi=100
        )

        fig.subplots_adjust(0, 0, 1, 1)
        # Svart bakgrund
        fig.patch.set_facecolor("#000000")
        ax.set_facecolor("#000000")

        ax.set_xlim(self.bounds[0], self.bounds[1])
        ax.set_ylim(self.bounds[2], self.bounds[3])
        ax.set_aspect("equal")
        ax.axis("off")

        self.bounds = self.calculate_bounds()


        if with_map:
            if folder == 'frames_cityLines':
                fig.patch.set_facecolor("#101216")
                ax.set_facecolor("#101216")

                # Vår egenritade karta
                self.draw_map(ax)

            else:
                ctx.add_basemap(
                    ax,
                    source=ctx.providers.Esri.WorldStreetMap,
                    crs="EPSG:3857",
                    attribution=False
                )
                fig.patch.set_facecolor("white")


        if folder == 'frames_map':
            textColor = 'black'
        else:
            textColor = 'white'

        line, = ax.plot(
            [], [],
            color=self.ROUTE_COLOR,
            linewidth=2,
            solid_capstyle="round",
            zorder=10
        )
        marker, = ax.plot(
            [], [],
            marker="o",
            color=self.ROUTE_COLOR,
            markersize=5,
            zorder=11
        )

        # ---------------


        # Beräkna timmar, minuter och sekunder
        total_seconds = int(self.total_time_seconds)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        time_numbers = ax.text(
            0.25, 0.05,
            f"{hours:02d}:{minutes:02d}:{seconds:02d}",
            transform=ax.transAxes,
            fontsize=20,
            fontweight="bold",
            color=textColor,
            ha="center",
            va="center",
            zorder=20
        )

        time_text = ax.text(
            0.25, 0.08,
            "TOTAL TIME",
            transform=ax.transAxes,
            fontsize=20,
            fontweight="bold",
            color=self.ROUTE_COLOR,
            ha="center",
            va="center",
            zorder=20
        )
        distance_numbers = ax.text(
            0.75, 0.05,
            f"{self.distance_km[-1]:.1f} km",
            transform=ax.transAxes,
            fontsize=20,
            fontweight="bold",
            color=textColor,
            ha="center",
            va="center",
            zorder=20
        )

        distance_text = ax.text(
            0.75, 0.08,
            "TOTAL DISTANCE",
            transform=ax.transAxes,
            fontsize=20,
            fontweight="bold",
            color=self.ROUTE_COLOR,
            ha="center",
            va="center",
            zorder=20
        )

        max_speed_nummer = ax.text(
            0.75, 0.15,
            f"{self.max_speed_kmh} km/h",
            transform=ax.transAxes,
            fontsize=20,
            fontweight="bold",
            color=textColor,
            ha="center",
            va="center",
            zorder=20
        )

        max_speed_text = ax.text(
            0.75, 0.18,
            f"MAX SPEED",
            transform=ax.transAxes,
            fontsize=20,
            fontweight="bold",
            color=self.ROUTE_COLOR,
            ha="center",
            va="center",
            zorder=20
        )

        type_of_surf_text = ax.text(
            0.25, 0.18,
            f"TYPE OF SURF",
            transform=ax.transAxes,
            fontsize=20,
            fontweight="bold",
            color=self.ROUTE_COLOR,
            ha="center",
            va="center",
            zorder=20
        )
        ax.text(
            0.25, 0.15,
            self.mailData['surfType'].upper(),
            transform=ax.transAxes,
            fontsize=20,
            fontweight="bold",
            color=textColor,
            ha="center",
            va="center",
            zorder=20
        )

        ax.text(
            0.5, 0.95,
            f"{self.date}",
            transform=ax.transAxes,
            fontsize=20,
            fontweight="bold",
            color=self.ROUTE_COLOR,
            ha="center",
            va="center",
            zorder=20
        )

        ax.text(
            0.5, 0.91,
            self.mailData['title'],
            transform=ax.transAxes,
            fontsize=20,
            fontweight="bold",
            color=textColor,
            ha="center",
            va="center",
            zorder=20
        )

        return fig, line, marker, distance_numbers, time_numbers

    def draw_map(self, ax):
        import osmnx as ox

        # Kartgränser i EPSG:3857
        west_x, east_x, south_y, north_y = self.bounds

        # Konvertera till latitud/longitud
        transformer = Transformer.from_crs(
            "EPSG:3857",
            "EPSG:4326",
            always_xy=True
        )

        west, south = transformer.transform(
            west_x, south_y
        )

        east, north = transformer.transform(
            east_x, north_y
        )

        bbox = (west, south, east, north)

        # 1. Hämta och rita vägnät
        G = ox.graph_from_bbox(
            bbox,
            network_type="all",
            simplify=True
        )

        G = ox.project_graph(
            G,
            to_crs="EPSG:3857"
        )

        ox.plot_graph(
            G,
            ax=ax,
            node_size=0,
            edge_color="#454A50",
            edge_linewidth=0.7,
            bgcolor="#101216",
            show=False,
            close=False
        )
        for collection in ax.collections:
            collection.set_zorder(1)

        # 2. Hämta vattenkonturer
        try:
            water = ox.features_from_bbox(
                bbox,
                tags={
                    "natural": ["water", "coastline"],
                    "waterway": ["riverbank"]
                }
            )

            if not water.empty:
                water = water.to_crs("EPSG:3857")

                water.plot(
                    ax=ax,
                    facecolor="none",
                    edgecolor="#454A50",
                    linewidth=1.2,
                    zorder=2
                )

        except Exception as e:
            print(f"Kunde inte hämta vatten: {e}")

        # ---------------------------
        # 3. Återställ kartgränser
        # ---------------------------

        ax.set_xlim(west_x, east_x)
        ax.set_ylim(south_y, north_y)

        ax.set_aspect("equal")
        ax.axis("off")

    def calculate_bounds(self):
        # GPS-ruttens geografiska utbredning
        min_x, max_x = self.x.min(), self.x.max()
        min_y, max_y = self.y.min(), self.y.max()

        # Mittpunkt
        cx = (min_x + max_x) / 2
        cy = (min_y + max_y) / 2

        # Bildens proportioner
        aspect = self.WIDTH / self.HEIGHT

        # Rutten + 15 % marginal på varje sida
        route_width = max(max_x - min_x, 100) * 1.3
        route_height = max(max_y - min_y, 100) * 1.3

        # Anpassa till bildens proportioner
        width = max(route_width, route_height * aspect)
        height = width / aspect

        return (
            cx - width / 2,
            cx + width / 2,
            cy - height / 2,
            cy + height / 2
        )

    def count_distance(self, df):
        # Konvertera GPS-koordinater till radianer
        lat = np.radians(df["latitude"].to_numpy())
        lon = np.radians(df["longitude"].to_numpy())

        # Skillnaden mellan varje GPS-punkt
        dlat = np.diff(lat)
        dlon = np.diff(lon)

        # Haversine-formeln
        a = (
                np.sin(dlat / 2) ** 2
                + np.cos(lat[:-1]) * np.cos(lat[1:])
                * np.sin(dlon / 2) ** 2
        )

        R = 6371000  # Jordens radie i meter

        self.distances = 2 * R * np.arcsin(
            np.sqrt(np.clip(a, 0, 1))
        )

        # Ackumulerad distans i kilometer
        self.distance_km = np.concatenate((
            [0],
            np.cumsum(self.distances) / 1000
        ))

    def count_time(self, df):
        # Konvertera tidsstämplar till datetime
        timestamps = pd.to_datetime(df["time"], utc=True)

        # Antal sekunder från starten för varje GPS-punkt
        self.elapsed_seconds = (
                timestamps - timestamps.iloc[0]
        ).dt.total_seconds().to_numpy()
        self.total_time_seconds = self.elapsed_seconds[-1]

    def current_speed(self, df):
        # Tidsskillnad mellan GPS-punkterna (sekunder)
        time_diffs = np.diff(self.elapsed_seconds)

        # Hastighet i km/h
        self.speed_kmh = np.zeros(len(df))

        # Undvik division med noll
        valid = time_diffs > 0

        self.speed_kmh[1:] = np.divide(
            self.distances * 3.6,
            time_diffs,
            out=np.zeros_like(self.distances, dtype=float),
            where=valid
        )

        # Dina ursprungliga hastigheter
        speeds = pd.Series(self.speed_kmh)

        # Medianen av fem närliggande mätningar
        local_median = speeds.rolling(
            window=5,
            center=True,
            min_periods=3
        ).median()

        # Identifiera misstänkta hastighetstoppar
        outliers = (
                (speeds > local_median * 2.5) &
                ((speeds - local_median) > 20)
        )

        # Behåll originalet och skapa en filtrerad version
        self.filtered_speed_kmh = (
            speeds.mask(outliers)
            .interpolate()
            .bfill()
            .ffill()
            .to_numpy()
        )

    def max_speed_cal(self, df):
        max_speed = df["max_speed"].iloc[0]
        self.max_speed_kmh = max_speed * 3.6

    def add_overlay_image(self, ax, image_path):
        # Läs in PNG med alpha-kanal
        image = Image.open(image_path).convert("RGBA")

        # Skapa bildobjektet
        image_box = OffsetImage(
            np.asarray(image),
            zoom=0.5
        )

        # Placera bilden relativt till axeln
        overlay = AnnotationBbox(
            image_box,
            (0.5, 0.5),
            xycoords="axes fraction",
            frameon=False,
            zorder=30
        )

        ax.add_artist(overlay)

