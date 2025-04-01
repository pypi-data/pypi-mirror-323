import os
import sys
import shutil
from threading import Thread
from time import sleep as wait
from typing import Optional, Callable, List, Dict
import pygame
from mutagen.mp3 import MP3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Redirect stdout to suppress pygame and AltColor messages
old_stdout: Optional[object] = sys.stdout
sys.stdout = open(os.devnull, 'w')

# Initialize the pygame mixer
try:
    pygame.mixer.init()
except pygame.error as e:
    logger.error(f"Failed to initialize pygame mixer: {e}")
    sys.exit(1)

# Retrieve colored print
try:
    from altcolor import cPrint  # Custom color print module
except ImportError:
    logger.warning("altcolor module not found. Defaulting to standard prints.")
    cPrint = lambda color, text: print(text)

# Restore stdout
sys.stdout.close()
sys.stdout = old_stdout

# Global variables
music_on: bool = True  # Flag indicating if music playback is enabled
music_file: Optional[str] = None  # Currently playing music file
current_dir: str = os.path.dirname(__file__)  # Directory of the current script
playlist: List[str] = []  # List of music files for the playlist
sound_registry: Dict[str, pygame.mixer.Sound] = {}  # Cached sound effects

# User-configurable settings
default_volume: float = 0.5
music_directory: str = os.path.join(current_dir, "music")

def show_credits() -> None:
    """
    Display credits and license information for the program.
    """
    cPrint("BLUE", "\n\nThanks for using AudioBox! Check out our other products at 'https://tairerullc.vercel.app'")
    cPrint(
        "MAGENTA",
        "\n\nNote:\nThe music, not the sfx, is by Sadie Jean. The song is called 'Locksmith' and is available via Spotify."
        "\nPlease note this song is copyrighted material, and we use it only as an example. "
        "We are not endorsed by them, nor are they endorsed by us.\n\n"
    )
show_credits()

def generate_example_files() -> None:
    """
    Generate two example audio files for use by the program.
    """
    example_sfx: str = os.path.join(current_dir, "example_sfx.wav")
    example_music: str = os.path.join(current_dir, "example_music.mp3")

    cloned_sfx: str = "example_sfx.wav"
    cloned_music: str = "example_music.mp3"

    try:
        shutil.copyfile(example_sfx, cloned_sfx)
        shutil.copyfile(example_music, cloned_music)
        logger.info("Example files generated successfully.")
    except FileNotFoundError as e:
        logger.error(f"Error generating example files: {e}")
        cPrint("RED", f"Error generating example files: {e}")

def sfx(music_directory: Optional[str], filename: str, times: int = 1, volume: float = default_volume) -> None:
    """
    Play a sound effect a specified number of times with adjustable volume.

    Args:
        music_directory (Optional[str]): Directory containing audio files.
        filename (str): The base name of the sound effect file (without extension).
        times (int): Number of times to play the sound effect (default is 1).
        volume (float): Volume level for the sound effect (0.0 to 1.0).
    """
    def play_sound_effect() -> None:
        try:
            filepath: str = find_audio_file(filename) if music_directory is None else find_audio_file(music_directory, filename)
            if filename not in sound_registry:
                sound_registry[filename] = pygame.mixer.Sound(filepath)
            sound_effect = sound_registry[filename]
            sound_effect.set_volume(volume)
            sound_effect.play(loops=times - 1)
            logger.info(f"Playing sound effect: {filename}")
        except (pygame.error, FileNotFoundError) as e:
            logger.error(f"Error playing sound effect: {e}")
            cPrint("RED", f"Error playing sound effect: {e}")

    sound_thread: Thread = Thread(target=play_sound_effect)
    sound_thread.start()

def play_music(music_directory: Optional[str], filename: str, stop_other: bool = False, loop: bool = True, volume: float = default_volume) -> None:
    """
    Play background music, optionally stopping any currently playing music.

    Args:
        music_directory (Optional[str]): Directory containing audio files.
        filename (str): The base name of the music file (without extension).
        stop_other (bool): Whether to stop other currently playing music (default is False).
        loop (bool): Whether to loop the music (default is True).
        volume (float): Volume level for the music (0.0 to 1.0).
    """
    global music_file

    if not music_on:
        logger.warning("Music playback is disabled.")
        cPrint("YELLOW", "Music playback is disabled.")
        return

    filepath: str = find_audio_file(filename) if music_directory is None else find_audio_file(music_directory, filename)

    if pygame.mixer.music.get_busy() and music_file == filepath:
        logger.info("Music is already playing.")
        cPrint("YELLOW", "Music is already playing.")
        return  # Music already playing, no need to restart

    def play_and_wait() -> None:
        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play(-1 if loop else 0)
            pygame.mixer.music.set_volume(volume)
            music_file = filepath
            logger.info(f"Playing music: {filename}")

            while pygame.mixer.music.get_busy():
                wait(1)
        except pygame.error as e:
            logger.error(f"Error loading or playing music file: {e}")
            cPrint("RED", f"Error loading or playing music file: {e}")

    if stop_other:
        pygame.mixer.music.stop()

    music_thread: Thread = Thread(target=play_and_wait)
    music_thread.start()

def stop_music() -> None:
    """
    Stop the currently playing background music.
    """
    global music_file
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        music_file = None
        logger.info("Music playback stopped.")
        cPrint("BLUE", "Music playback stopped.")

def add_to_playlist(filename: str) -> None:
    """
    Add a music file to the playlist.

    Args:
        filename (str): The base name of the music file (without extension).
    """
    try:
        filepath: str = find_audio_file(filename)
        playlist.append(filepath)
        logger.info(f"Added to playlist: {filename}")
        cPrint("GREEN", f"Added to playlist: {filename}")
    except FileNotFoundError as e:
        logger.error(f"Error adding to playlist: {e}")
        cPrint("RED", f"Error adding to playlist: {e}")

def remove_from_playlist(filename: str) -> None:
    """
    Remove a music file from the playlist.

    Args:
        filename (str): The base name of the music file (without extension).
    """
    try:
        filepath: str = find_audio_file(filename)
        if filepath in playlist:
            playlist.remove(filepath)
            logger.info(f"Removed from playlist: {filename}")
            cPrint("GREEN", f"Removed from playlist: {filename}")
        else:
            raise FileNotFoundError(f"{filename} not found in playlist.")
    except FileNotFoundError as e:
        logger.error(f"Error removing from playlist: {e}")
        cPrint("RED", f"Error removing from playlist: {e}")

def clear_playlist() -> None:
    """
    Clear all music files from the playlist.
    """
    playlist.clear()
    logger.info("Playlist cleared.")
    cPrint("GREEN", "Playlist cleared.")

def play_playlist() -> None:
    """
    Play all music files in the playlist sequentially.
    """
    def play_songs() -> None:
        for song in playlist:
            if music_on:
                try:
                    pygame.mixer.music.load(song)
                    pygame.mixer.music.play()
                    logger.info(f"Playing song: {os.path.basename(song)}")
                    while pygame.mixer.music.get_busy():
                        wait(1)
                except pygame.error as e:
                    logger.error(f"Error playing song: {e}")
                    cPrint("RED", f"Error playing song: {e}")

    playlist_thread: Thread = Thread(target=play_songs)
    playlist_thread.start()

def find_audio_file(music_directory: Optional[str], filename: str) -> str:
    """
    Locate an audio file with .wav or .mp3 extension.

    Args:
        music_directory (Optional[str]): Directory containing audio files.
        filename (str): The base name of the file to locate.

    Returns:
        str: The full path to the located audio file.

    Raises:
        FileNotFoundError: If neither a .wav nor .mp3 file with the given base name is found.
    """
    if os.path.isabs(filename):
        return filename  # Absolute path provided

    wav_file: str = os.path.join(music_directory, f"{filename}.wav") if music_directory else f"{filename}.wav"
    mp3_file: str = os.path.join(music_directory, f"{filename}.mp3") if music_directory else f"{filename}.mp3"

    if os.path.isfile(wav_file):
        return wav_file
    elif os.path.isfile(mp3_file):
        return mp3_file
    else:
        raise FileNotFoundError(f"File {filename}.wav or {filename}.mp3 not found.")

def get_audio_length(filename: str) -> float:
    """
    Retrieve the length of an audio file in seconds.

    Args:
        filename (str): The base name of the audio file (without extension).

    Returns:
        float: The length of the audio file in seconds.

    Raises:
        FileNotFoundError: If the audio file is not found.
        ValueError: If the audio file format is unsupported.
    """
    try:
        filepath: str = find_audio_file(filename)
        if filepath.endswith(".wav"):
            sound = pygame.mixer.Sound(filepath)
            return sound.get_length()
        elif filepath.endswith(".mp3"):
            audio = MP3(filepath)
            return audio.info.length
        else:
            raise ValueError("Unsupported file format. Only .wav and .mp3 are supported.")
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Error retrieving audio length: {e}")
        cPrint("RED", f"Error retrieving audio length: {e}")
        raise FileNotFoundError(f"File {filename}.wav or {filename}.mp3 not found.")