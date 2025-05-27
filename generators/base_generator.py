"""
Base class for all MIDI generators in the benchmark suite.
This class provides common functionality for MIDI file generation and management.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import mido

class MIDIGenerator:
    """Base class for all MIDI generators in the benchmark suite."""
    
    def __init__(self, output_dir: str):
        """Initialize the generator with an output directory.
        
        Parameters
        ----------
        output_dir : str
            Directory where generated MIDI files will be saved
        """
        self.output_dir = Path(output_dir)
        if not self.output_dir.exists():
            raise ValueError(f"Output directory {self.output_dir} does not exist")
        
        # Common MIDI settings
        self.default_tempo = 500000  # 120 BPM
        self.default_ticks_per_beat = 480
        
        # Common note mappings
        self.notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    def _create_midi_file(self, ticks_per_beat: Optional[int] = None) -> mido.MidiFile:
        """Create a new MIDI file with default settings.
        
        Parameters
        ----------
        ticks_per_beat : int, optional
            Number of ticks per beat. If None, uses default_ticks_per_beat
            
        Returns
        -------
        mido.MidiFile
            A new MIDI file instance
        """
        if ticks_per_beat is None:
            ticks_per_beat = self.default_ticks_per_beat
            
        mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
        track = mido.MidiTrack()
        mid.tracks.append(track)
        
        # Set default tempo
        track.append(mido.MetaMessage('set_tempo', tempo=self.default_tempo, time=0))
        
        return mid
    
    def _get_note_name(self, midi_note: int) -> str:
        """Get a human-readable note name from MIDI note number. Defaults to using sharp names only.
        
        Parameters
        ----------
        midi_note : int
            MIDI note number (0-127)
            
        Returns
        -------
        str
            Note name with octave (e.g., "C4")
        """
        octave = (midi_note // 12) - 1
        note = self.notes[midi_note % 12]
        return f"{note}{octave}"
    
    def _save_midi_file(self, mid: mido.MidiFile, filename: str) -> str:
        """Save a MIDI file to the output directory.
        
        Parameters
        ----------
        mid : mido.MidiFile
            The MIDI file to save
        filename : str
            Name of the file to save
            
        Returns
        -------
        str
            Path to the saved file
        """
        output_path = self.output_dir / filename
        mid.save(str(output_path))
        return str(output_path)
    
    def _add_note(self, track: mido.MidiTrack, note: int, 
                  velocity: int = 80, time: int = 0, duration: int = 480) -> None:
        """Add a note to a MIDI track.
        
        Parameters
        ----------
        track : mido.MidiTrack
            The track to add the note to
        note : int
            MIDI note number
        velocity : int, optional
            Note velocity (0-127), by default 80
        time : int, optional
            Time before the note starts, by default 0
        duration : int, optional
            Duration of the note in ticks, by default 480 (quarter note)
        """
        track.append(mido.Message('note_on', note=note, velocity=velocity, time=time))
        track.append(mido.Message('note_off', note=note, velocity=0, time=duration))
    
    def _add_chord(self, track: mido.MidiTrack, notes: List[int], 
                   velocity: int = 80, time: int = 0, duration: int = 480) -> None:
        """Add multiple notes simultaneously (a chord) to a MIDI track.
        
        Parameters
        ----------
        track : mido.MidiTrack
            The track to add the chord to
        notes : List[int]
            List of MIDI note numbers to play simultaneously
        velocity : int, optional
            Note velocity (0-127), by default 80
        time : int, optional
            Time before the chord starts, by default 0
        duration : int, optional
            Duration of the chord in ticks, by default 480 (quarter note)
        """
        # Add all note_on messages with the same time value
        for note in notes:
            track.append(mido.Message('note_on', note=note, velocity=velocity, time=time))
            time = 0  # Only the first note gets the initial time value
        
        # Add all note_off messages
        track.append(mido.Message('note_off', note=notes[0], velocity=0, time=duration))
        for note in notes[1:]:
            track.append(mido.Message('note_off', note=note, velocity=0, time=0)) 