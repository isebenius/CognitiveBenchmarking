"""
This script generates transposed versions of MIDI files by transposing specific tracks up or down.
"""

from pathlib import Path
from typing import Union, List, Optional
import mido
from .base_generator import MIDIGenerator

class TrackTranspositionGenerator(MIDIGenerator):
    """Generate transposed versions of MIDI files by transposing specific tracks."""
    
    def __init__(self, output_dir: str = "track_transposition_examples"):
        """Initialize the generator.
        
        Parameters
        ----------
        output_dir : str, optional
            Directory to save generated MIDI files, by default "track_transposition_examples"
        """
        super().__init__(output_dir)
    
    def generate_transposed_versions(
        self,
        input_midi_path: Union[str, Path],
        track_indices: List[int],
        semitones: int = 1,
        verbose: bool = False
    ) -> dict[str, List[str]]:
        """Generate transposed versions of specific tracks in a MIDI file.
        
        Parameters
        ----------
        input_midi_path : Union[str, Path]
            Path to the input MIDI file
        track_indices : List[int]
            List of track indices to transpose (0-based)
        semitones : int, optional
            Number of semitones to transpose by (positive = up, negative = down), by default 1
        verbose : bool, optional
            Whether to print progress information, by default False
            
        Returns
        -------
        dict[str, List[str]]
            Dictionary with a single key 'paths' containing a list of all generated file paths
        """
        input_path = Path(input_midi_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input MIDI file not found: {input_path}")
        
        # Load MIDI file to check number of tracks
        midi_file = mido.MidiFile(str(input_path))
        num_tracks = len(midi_file.tracks)
        
        # Validate track indices
        for track_idx in track_indices:
            if track_idx < 0 or track_idx >= num_tracks:
                raise ValueError(f"Invalid track index {track_idx}. File has {num_tracks} tracks.")
        
        # Generate transposed versions for each track
        output_paths = []
        for track_idx in track_indices:
            # Generate both up and down transpositions
            for direction, semitone_offset in [("up", semitones), ("down", -semitones)]:
                # Create output filename
                output_filename = f"{input_path.stem}_track{track_idx}_{direction}{abs(semitones)}{input_path.suffix}"
                output_path = self.output_dir / output_filename
                
                # Generate transposed version
                transpose_track(
                    midi_file_path=str(input_path),
                    output_path=str(output_path),
                    track_index=track_idx,
                    semitones=semitone_offset
                )
                
                output_paths.append(str(output_path))
                
                if verbose:
                    print(f"Generated {direction} transposition for track {track_idx}: {output_path}")
        
        return {"paths": output_paths}

def transpose_track(midi_file_path, output_path, track_index, semitones):
    """
    Load a MIDI file and transpose a specific track by a given number of semitones.
    
    Args:
        midi_file_path (str): Path to input MIDI file
        output_path (str): Path for output MIDI file
        track_index (int): Index of track to transpose (0-based)
        semitones (int): Number of semitones to transpose (positive = up, negative = down)
    """
    # Load the MIDI file
    mid = mido.MidiFile(midi_file_path)
    
    # Check if track index is valid
    if track_index >= len(mid.tracks):
        raise ValueError(f"Track index {track_index} out of range. File has {len(mid.tracks)} tracks.")
    
    # Create a copy to avoid modifying the original
    new_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
    
    for i, track in enumerate(mid.tracks):
        new_track = mido.MidiTrack()
        
        for msg in track:
            # Copy the message
            new_msg = msg.copy()
            
            # If this is the track to transpose and the message has a note
            if i == track_index and hasattr(msg, 'note') and msg.type in ['note_on', 'note_off']:
                # Transpose the note, ensuring it stays within MIDI range (0-127)
                new_note = max(0, min(127, msg.note + semitones))
                new_msg.note = new_note
            
            new_track.append(new_msg)
        
        new_mid.tracks.append(new_track)
    
    # Save the transposed MIDI file
    new_mid.save(output_path)
    print(f"Transposed track {track_index} by {semitones} semitones. Saved to {output_path}")

# Example usage:
# generator = TrackTranspositionGenerator(output_dir="path/to/output")
# result = generator.generate_transposed_versions(
#     input_midi_path="path/to/input.mid",
#     track_indices=[0, 1],  # Transpose tracks 0 and 1
#     semitones=2,  # Transpose up/down by 2 semitones
#     verbose=True
# )
# # Access all paths: result["paths"]
