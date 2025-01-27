import os
import requests
from tqdm import tqdm
from colorama import Fore, Style, init
import logging
import coloredlogs
import platform
from pymediainfo import MediaInfo

init(autoreset=True)

logger = logging.getLogger(Fore.GREEN + "+ HELPER + ")
coloredlogs.install(level='DEBUG', logger=logger)

# =========================================================================================================== #

binaries = {
    "Windows": [
        "https://github.com/ThatNotEasy/DDownloader/raw/refs/heads/main/DDownloader/bin/N_m3u8DL-RE.exe",
        "https://github.com/ThatNotEasy/DDownloader/raw/refs/heads/main/DDownloader/bin/ffmpeg.exe",
        "https://github.com/ThatNotEasy/DDownloader/raw/refs/heads/main/DDownloader/bin/aria2c.exe",
        "https://github.com/ThatNotEasy/DDownloader/raw/refs/heads/main/DDownloader/bin/mp4decrypt.exe",
        "https://github.com/ThatNotEasy/DDownloader/raw/refs/heads/main/DDownloader/bin/shaka-packager.exe",
        "https://github.com/ThatNotEasy/DDownloader/raw/refs/heads/main/DDownloader/bin/yt-dlp.exe",
        "https://github.com/ThatNotEasy/DDownloader/raw/refs/heads/main/DDownloader/bin/mkvmerge.exe"
    ],
    "Linux": [
        "https://github.com/ThatNotEasy/DDownloader/raw/refs/heads/main/DDownloader/bin/N_m3u8DL-RE"
    ]
}

# =========================================================================================================== #

def download_binaries(bin_dir, platform_name):
    os.makedirs(bin_dir, exist_ok=True)
    logger.info(f"Platform detected: {platform_name}")
    logger.info(f"Using binary directory: {bin_dir}")
    
    platform_binaries = binaries.get(platform_name, [])
    
    if not platform_binaries:
        logger.error(f"No binaries available for platform: {platform_name}")
        return

    for binary_url in platform_binaries:
        try:
            filename = binary_url.split("/")[-1]
            filepath = os.path.join(bin_dir, filename)

            if os.path.exists(filepath):
                logger.info(f"{Style.BRIGHT}{Fore.YELLOW}Skipping {filename} (already exists).")
                continue

            logger.info(f"{Fore.GREEN}Downloading {Fore.WHITE}{filename}...{Fore.RESET}")
            response = requests.get(binary_url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            with open(filepath, "wb") as file, tqdm(
                total=total_size,
                unit='B',
                unit_scale=True,
                desc=f"{Fore.CYAN}{filename}{Fore.RESET}",
                dynamic_ncols=True,
                bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} [{rate_fmt}]"
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    progress_bar.update(len(chunk))

            if platform_name == "Linux":
                os.chmod(filepath, 0o755)
        except requests.exceptions.RequestException as e:
            logger.error(f"{Fore.RED}Failed to download {binary_url}: {e}{Fore.RESET}")
        except Exception as e:
            logger.error(f"{Fore.RED}Unexpected error for {binary_url}: {e}{Fore.RESET}")

# =========================================================================================================== #

def detect_platform():
    system_platform = platform.system().lower()
    if system_platform == 'windows':
        return 'Windows'
    elif system_platform == 'linux':
        return 'Linux'
    elif system_platform == 'darwin':
        return 'MacOS'
    else:
        return 'Unknown'

# =========================================================================================================== #

def get_media_info(file_path):
    try:
        logger.info(f"Parsing media file: {file_path}")
        media_info = MediaInfo.parse(file_path)
        result = {"file_path": file_path, "tracks": []}

        for track in media_info.tracks:
            track_info = {"track_type": track.track_type}

            if track.track_type == "Video":
                track_info.update({
                    "codec": track.codec,
                    "width": track.width,
                    "height": track.height,
                    "frame_rate": track.frame_rate,
                    "bit_rate": track.bit_rate,
                    "duration": track.duration,
                    "aspect_ratio": track.display_aspect_ratio,
                })
            elif track.track_type == "Audio":
                track_info.update({
                    "codec": track.codec,
                    "channels": track.channel_s,
                    "sample_rate": track.sampling_rate,
                    "bit_rate": track.bit_rate,
                    "duration": track.duration,
                    "language": track.language,
                })
            elif track.track_type == "Text":
                track_info.update({
                    "language": track.language,
                    "format": track.format,
                })
            elif track.track_type == "General":
                track_info.update({
                    "file_size": track.file_size,
                    "format": track.format,
                    "duration": track.duration,
                    "overall_bit_rate": track.overall_bit_rate,
                })

            result["tracks"].append(track_info)

        logger.info(f"Successfully extracted media information for: {file_path}")
        return result

    except Exception as e:
        logger.error(f"Error occurred while parsing media file '{file_path}': {e}")
        return None
    
# =========================================================================================================== #
