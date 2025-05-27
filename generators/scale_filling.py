"""
This script generates stimuli beginning with a roto triad, then provides all possible scale variations 
with fixed anchor notes and variable non-anchor notes.
It then saves the generated MIDI files to the output directory.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import itertools
import mido
import random
from .base_generator import MIDIGenerator

class ScaleFillingGenerator(MIDIGenerator):
    """Generate all possible scale variations with fixed anchor notes and variable non-anchor notes."""
    
    def __init__(self, output_dir: str = "scale_examples"):
        """Initialize the generator."""
        super().__init__(output_dir)
        
        # Key name to semitone offset (from C)
        self.key_offsets = {
            "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, 
            "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, 
            "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
        }
        
        # Scale intervals (semitones from tonic)
        self.major_scale = [0, 2, 4, 5, 7, 9, 11, 12]  # Eight notes including octave
        self.minor_scale = [0, 2, 3, 5, 7, 8, 10, 12]  # Natural minor with octave
        
        # Anchor positions (0-indexed - tonic, mediant, dominant, octave)
        self.anchor_positions = [0, 2, 4, 7]
        
        # Alternative notes for each non-anchor position (0-indexed)
        # For position 1 (second note): flat 2, natural 2, sharp 2
        # For position 3 (fourth note): perfect 4, augmented 4
        # For position 5 (sixth note): minor 6, major 6
        # For position 6 (seventh note): minor 7, major 7
        self.alternatives = {
            1: [1, 2, 3],     # Semitones above root for position 1
            3: [5, 6],        # Semitones above root for position 3
            5: [8, 9],        # Semitones above root for position 5
            6: [10, 11]       # Semitones above root for position 6
        }
    
    def generate_all_scale_variations(self, key_name: str = "C", mode: str = "major"):
        """Generate all possible scale variations with the specified alternatives.
        
        Parameters
        ----------
        key_name : str
            Key name (e.g., "C", "G", "F#")
        mode : str
            Scale mode ("major" or "minor")
            
        Returns
        -------
        List[str]
            Paths to all generated MIDI files
        """
        # Get key offset from C
        key_offset = self.key_offsets.get(key_name, 0)
        
        # Select base scale intervals based on mode
        base_scale_intervals = self.major_scale if mode.lower() == "major" else self.minor_scale
        
        # Calculate root note (middle C + key offset)
        root_note = 60 + key_offset
        
        # Get all possible combinations for non-anchor positions
        # For each position, we need to try each alternative
        alternatives_pos1 = self.alternatives[1]
        alternatives_pos3 = self.alternatives[3]
        alternatives_pos5 = self.alternatives[5]
        alternatives_pos6 = self.alternatives[6]
        
        all_combinations = list(itertools.product(
            alternatives_pos1,
            alternatives_pos3,
            alternatives_pos5,
            alternatives_pos6
        ))
        
        # For each combination, generate a MIDI file
        generated_paths = []
        
        for combo in all_combinations:
            # Create scale intervals for this combination
            scale_intervals = base_scale_intervals.copy()
            
            # Replace non-anchor positions with alternatives
            scale_intervals[1] = combo[0]  # Position 1 (second note)
            scale_intervals[3] = combo[1]  # Position 3 (fourth note)
            scale_intervals[5] = combo[2]  # Position 5 (sixth note)
            scale_intervals[6] = combo[3]  # Position 6 (seventh note)
            
            # Check if this is the correct scale (matches base scale)
            is_correct = (scale_intervals == base_scale_intervals)
            
            # Generate MIDI file for this scale variation
            output_path = self._generate_midi(key_name, mode, root_note, scale_intervals, combo, is_correct)
            generated_paths.append(output_path)
        
        return generated_paths
    
    def _generate_midi(self, key_name, mode, root_note, scale_intervals, combo, is_correct):
        """Generate a MIDI file for a specific scale variation.
        
        Parameters
        ----------
        key_name : str
            Key name
        mode : str
            Scale mode
        root_note : int
            MIDI note number of the root
        scale_intervals : List[int]
            Scale intervals for this variation
        combo : tuple
            The specific combination of alternatives used
        is_correct : bool
            Whether this is the correct/standard scale
            
        Returns
        -------
        str
            Path to the generated MIDI file
        """
        # Create a new MIDI file
        mid = self._create_midi_file()
        track = mid.tracks[0]
        
        # Create the triad - get 1st, 3rd, and 5th of the scale
        # For the triad, always use the standard scale degrees
        base_scale = self.major_scale if mode.lower() == "major" else self.minor_scale
        triad_notes = [
            root_note,                # Root
            root_note + base_scale[2],  # Third
            root_note + base_scale[4]   # Fifth
        ]
        
        # Add triad notes (all start simultaneously)
        self._add_chord(track, triad_notes, velocity=80, time=0, duration=480)
        
        # Add a brief rest
        rest_time = 960  # Half note rest
        
        # Generate the scale notes based on the provided intervals
        scale_notes = [root_note + interval for interval in scale_intervals]
        
        # Add scale notes as eighth notes
        for i, note in enumerate(scale_notes):
            # First note comes after the rest, others follow immediately
            time_value = rest_time if i == 0 else 0
            
            # Add note
            self._add_note(track, note, velocity=70, time=time_value, duration=240)  # Eighth note
        
        # Create a descriptive filename
        # Format: Key_Mode_p1-X_p3-X_p5-X_p7-X.mid where X represents the semitone value
        variant_desc = f"p1-{combo[0]}_p3-{combo[1]}_p5-{combo[2]}_p7-{combo[3]}"
        correct_marker = "_correct" if is_correct else ""
        filename = f"{key_name}_{mode.lower()}_scale_{variant_desc}{correct_marker}.mid"
        
        return self._save_midi_file(mid, filename)

if __name__ == "__main__":
    import pathlib
    output_dir = pathlib.Path(__file__).parent.resolve() / "../data/examples/ScaleExamples" 
    generator = ScaleFillerGenerator(output_dir)
    generator.generate_all_scale_variations()