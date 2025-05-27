"""
This script generates all possible triad resolutions for a given backbone progression.
It then saves the generated MIDI files to the output directory.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from midigen.notes import Note
from midigen.keys import Key, Mode
from midigen.time import TimeSignature, Measure
from midigen.sequencer import Song, Track
import mido
import random
from .base_generator import MIDIGenerator

class CadenceGenerator(MIDIGenerator):
    """Generate cadence sequences with all possible triad resolutions."""
    
    def __init__(self, output_dir: str = "cadence_examples"):
        """Initialize the generator."""
        super().__init__(output_dir)
        
        # All chromatic notes
        self.all_notes = [
            Note.C, Note.Db, Note.D, Note.Eb, Note.E, Note.F,
            Note.Gb, Note.G, Note.Ab, Note.A, Note.Bb, Note.B
        ]
        
        # Triad types to test
        self.triad_types = [Mode.Major, Mode.Minor, Mode.Diminished]
        
        # Mode to simple name mapping
        self.mode_names = {
            Mode.Major: "maj",
            Mode.Minor: "min",
            Mode.Diminished: "dim"
        }
        
        # Note name mapping for filenames
        self.note_names = {
            Note.C: "C", Note.Db: "Db", Note.D: "D", Note.Eb: "Eb", Note.E: "E",
            Note.F: "F", Note.Gb: "Gb", Note.G: "G", Note.Ab: "Ab", Note.A: "A",
            Note.Bb: "Bb", Note.B: "B", Note.F_SHARP: "F#", Note.C_SHARP: "C#",
            Note.G_SHARP: "G#", Note.D_SHARP: "D#", Note.A_SHARP: "A#"
        }
        
        # Reverse mapping
        self.note_map = {
            "C": Note.C, "G": Note.G, "D": Note.D, "A": Note.A, "E": Note.E, 
            "B": Note.B, "F#": Note.F_SHARP, "Gb": Note.Gb, "Db": Note.Db, 
            "Ab": Note.Ab, "Eb": Note.Eb, "Bb": Note.Bb, "F": Note.F
        }
        
        # Numeric values for each note (0-11)
        self.note_values = {
            Note.C: 0, Note.Db: 1, Note.D: 2, Note.Eb: 3, Note.E: 4, Note.F: 5,
            Note.Gb: 6, Note.G: 7, Note.Ab: 8, Note.A: 9, Note.Bb: 10, Note.B: 11,
            Note.C_SHARP: 1, Note.D_SHARP: 3, Note.F_SHARP: 6, Note.G_SHARP: 8, Note.A_SHARP: 10
        }
    
    def get_halfsteps_from_tonic(self, tonic: Note, note: Note) -> int:
        """Calculate the number of half steps from the tonic to a given note.
        
        Parameters
        ----------
        tonic : Note
            The tonic note of the key
        note : Note
            The note to calculate distance to
            
        Returns
        -------
        int
            Number of half steps (0-11) from tonic to note
        """
        tonic_val = self.note_values.get(tonic, 0)
        note_val = self.note_values.get(note, 0)
        
        # Calculate the distance in half steps (0-11)
        return (note_val - tonic_val) % 12
    
    def get_roman_numeral(self, degree: int, chord_mode: Mode) -> str:
        """Get the appropriate Roman numeral for a scale degree and chord quality.
        
        Parameters
        ----------
        degree : int
            Scale degree (1-7)
        chord_mode : Mode
            The chord quality (major, minor, diminished)
            
        Returns
        -------
        str
            Roman numeral representation
        """
        roman_base = ["I", "II", "III", "IV", "V", "VI", "VII"]
        
        if 1 <= degree <= 7:
            numeral = roman_base[degree - 1]
            
            # Adjust case and add symbols based on mode
            if chord_mode == Mode.Minor:
                return numeral.lower()
            elif chord_mode == Mode.Diminished:
                return numeral.lower() + "°"
            else:  # Major
                return numeral
        
        return str(degree)  # Fallback
    
    def generate_all_resolutions(self, 
                               key_name: str = "C", 
                               backbone_progression: List[int] = None) -> Dict[str, Any]:
        """Generate cadence examples with all possible triad resolutions.
        
        Parameters
        ----------
        key_name : str
            Key of the progression (e.g., "C", "G", "F#")
        backbone_progression : List[int], optional
            Custom backbone chord progression using scale degrees, by default [1, 4, 1, 5]
            
        Returns
        -------
        Dict[str, Any]
            Paths to the generated MIDI files for each resolution
        """
        key_note = self.note_map.get(key_name, Note.C)
        key = Key(key_note, Mode.Major)
        
        # Define the backbone progression
        if backbone_progression is None:
            backbone_progression = [1, 4, 1, 5]  # Default I-IV-I-V
        
        time_signature = TimeSignature(1, 4)
        tempo = 100
        
        # Create the backbone chords
        backbone_chords = []
        backbone_numerals = []  # Store the Roman numerals
        prev_chord = None
        
        for degree in backbone_progression:
            # Get the relative key for this degree
            rel_key = key.relative_key(degree)
            
            # Determine the mode of this chord based on the key
            if degree in [1, 4, 5]:  # Major chords in major key
                chord_mode = Mode.Major
            elif degree in [2, 3, 6]:  # Minor chords in major key
                chord_mode = Mode.Minor
            elif degree == 7:  # Diminished chord in major key
                chord_mode = Mode.Diminished
            else:
                chord_mode = Mode.Major  # Default
            
            # Get the Roman numeral
            roman = self.get_roman_numeral(degree, chord_mode)
            backbone_numerals.append(roman)
            
            # Create the chord
            chord = rel_key.chord(
                match_voicing=prev_chord if prev_chord else key.triad()
            )
            backbone_chords.append(chord)
            prev_chord = chord
        
        # Last backbone chord is what we'll resolve from
        last_chord = backbone_chords[-1]
        
        # Generate a version for each possible resolution
        paths = {}
        
        # For each chromatic note
        for note in self.all_notes:
            # For each triad type
            for mode in self.triad_types:
                # Create a triad of this type on this root
                resolution_key = Key(note, mode)
                
                # Get the triad (chord built on scale degree 1)
                final_chord = resolution_key.relative_key(1).chord(match_voicing=last_chord)
                
                # Create the complete progression
                all_chords = backbone_chords.copy()
                all_chords.append(final_chord)
                
                # Convert to measures
                measures = []
                for chord in all_chords:
                    measure = Measure.from_pattern(
                        pattern=[chord] * time_signature.numerator,
                        time_signature=time_signature,
                        velocity=80
                    )
                    measures.append(measure)
                
                # Create track and save MIDI
                track = Track.from_measures(measures)
                
                # Get mode name
                mode_name = self.mode_names.get(mode, "unknown")
                
                # Calculate half steps from tonic
                half_steps = self.get_halfsteps_from_tonic(key_note, note)
                
                # Create chord label using half steps
                chord_label = f"{half_steps}_{mode_name}"
                
                # Create a filename that shows the backbone and then the resolution
                progression_string = "-".join(backbone_numerals)
                filename = f"{key_name}_from_{progression_string}_to_{chord_label}.mid"
                
                song = Song([track])
                output_path = self.output_dir / filename
                song.to_midi(str(output_path), tempo=tempo)
                
                # Store the path
                if chord_label not in paths:
                    paths[chord_label] = str(output_path)
        
        return {
            "key": key_name,
            "backbone": backbone_progression,
            "backbone_numerals": backbone_numerals,
            "paths": paths
        }
    
if __name__ == "__main__":
    import pathlib
    output_dir = pathlib.Path(__file__).parent.resolve() / "../data/examples/cadence_examples" 
    generator = CadenceGenerator(output_dir)
    generator.generate_all_resolutions()
