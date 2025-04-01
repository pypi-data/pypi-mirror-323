# AudioBox

AudioBox allows the user to play music and sound effects on any platform as long as you have the files.

## Latest Updates: 
* Added custom file paths for audio (optional)

## Installation

Install via pip:

```bash
pip install audiobox
```

## Example Code: 

```python
from time import sleep as wait
import audiobox

# Generate example files
audiobox.generate_example_files()

# Play sound effect in a separate thread
audiobox.sfx(filename="example_sfx", times=1, volume=0.5)
wait(audiobox.get_audio_length(filename="example_sfx"))

# Play music with looping enabled
audiobox.play_music(filename="example_music", stop_other=True, loop=True)

# Wait for the duration of the music
wait(audiobox.get_audio_length(filename="example_music"))

# Manage playlist: Add, Remove, Clear
audiobox.add_to_playlist(filename="example_music")
audiobox.play_playlist()
audiobox.remove_from_playlist(filename="example_music")
audiobox.clear_playlist()
```

## Links: 
### Website: https://tairerullc.vercel.app/

#### Contact 'tairerullc@gmail.com' for any inquiries, and we will get back to you at our earliest convenience. Thank you for using our product, and happy coding!