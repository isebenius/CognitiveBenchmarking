"""
This script generates stimuli of all possible intervals from a given starting note.
It then saves the generated MIDI files to the output directory.
This can be used easily to test transposition invariance - if profiles of intervallic expectedness are unchanges for adjacent notes.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import mido
import random
from .base_generator import MIDIGenerator

class IntervalLikelihoodGenerator(MIDIGenerator):
    """Generate examples to test transposition invariance - if musical concepts apply across all pitches."""
    
    def __init__(self, output_dir="transposition_tests"):
        """Initialize the generator."""
        super().__init__(output_dir)
        
        # Define intervals from -12 to +12 (octave below to octave above)
        self.interval_names = {
            -12: "neg_octave", -11: "neg_maj7", -10: "neg_min7", -9: "neg_maj6", 
            -8: "neg_min6", -7: "neg_p5", -6: "neg_tritone", -5: "neg_p4",
            -4: "neg_maj3", -3: "neg_min3", -2: "neg_maj2", -1: "neg_min2",
            0: "unison", 
            1: "min2", 2: "maj2", 3: "min3", 4: "maj3", 5: "p4", 6: "tritone",
            7: "p5", 8: "min6", 9: "maj6", 10: "min7", 11: "maj7", 12: "octave"
        }
        
        # Note range for starting pitches (C3 to C5)
        self.note_range = range(48, 73)  # MIDI notes 48-72
    
    def generate_all_intervals(self, start_note, context_interval=None, context_count=3):
        """Generate test files for all possible intervals from a starting note.
        
        Parameters
        ----------
        start_note : int
            MIDI note number to start from
        context_interval : int, optional
            If provided, adds context examples of this interval before the test
        context_count : int, optional
            Number of context examples to include (if context_interval is provided)
            
        Returns
        -------
        dict
            Dictionary mapping interval values to file paths
        """
        results = {}
        
        # Get context examples if specified
        context_examples = []
        if context_interval is not None:
            # Generate random starting notes for context examples
            available_notes = list(self.note_range)
            # Remove the test note and adjacent notes to avoid confusion
            for n in range(start_note-2, start_note+3):
                if n in available_notes:
                    available_notes.remove(n)
            
            if len(available_notes) >= context_count:
                context_notes = random.sample(available_notes, context_count)
                
                # Create the context examples
                for note in context_notes:
                    end_note = note + context_interval
                    # Skip if outside MIDI range
                    if 0 <= end_note <= 127:
                        context_examples.append((note, end_note))
        
        # Create examples for all intervals (-12 to +12 semitones)
        for interval in range(-12, 13):
            # Calculate the ending note
            end_note = start_note + interval
            
            # Skip if outside MIDI range
            if not (0 <= end_note <= 127):
                continue
            
            # Generate MIDI file
            interval_name = self.interval_names.get(interval, f"int{interval}")
            output_path = self._create_midi(
                start_note=start_note,
                end_note=end_note,
                interval=interval,
                context_examples=context_examples,
                interval_name=interval_name
            )
            
            results[interval] = output_path
        
        return results
    
    def _create_midi(self, start_note, end_note, interval, context_examples, interval_name):
        """Create a MIDI file with a specific interval, optionally with context examples.
        
        Parameters
        ----------
        start_note : int
            Starting MIDI note number
        end_note : int
            Ending MIDI note number
        interval : int
            Interval in semitones
        context_examples : list
            List of (start, end) note pairs for context examples
        interval_name : str
            Name of the interval for the filename
            
        Returns
        -------
        str
            Path to the generated MIDI file
        """
        # Create MIDI file
        mid = self._create_midi_file()
        track = mid.tracks[0]
        
        # Add context examples if provided
        for i, (ctx_start, ctx_end) in enumerate(context_examples):
            # First note of context example
            time_value = 480 if i == 0 else 240
            self._add_note(track, ctx_start, velocity=80, time=time_value, duration=480)
            
            # Second note of context example
            self._add_note(track, ctx_end, velocity=80, time=0, duration=480)
            
            # Pause between examples
            track.append(mido.Message('note_on', note=0, velocity=0, time=240))
            track.append(mido.Message('note_off', note=0, velocity=0, time=0))
        
        # Longer pause before test case if we had context examples
        time_value = 960 if context_examples else 480
        
        # Add test interval notes
        # First note
        self._add_note(track, start_note, velocity=90, time=time_value, duration=480)
        
        # Second note
        self._add_note(track, end_note, velocity=90, time=0, duration=480)
        
        # Create filename
        # Format: pitch{note}_{interval_name}.mid  (e.g., pitch60_p5.mid)
        note_name = self._get_note_name(start_note)
        filename = f"pitch{start_note}_{interval_name}.mid"
        if context_examples:
            # Add context info to filename if context was provided
            ctx_interval = context_examples[0][1] - context_examples[0][0]
            ctx_name = self.interval_names.get(ctx_interval, f"int{ctx_interval}")
            filename = f"pitch{start_note}_ctx{ctx_name}_{interval_name}.mid"
            
        return self._save_midi_file(mid, filename)
    
    def _get_note_name(self, midi_note):
        """Get a human-readable note name from MIDI note number."""
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = (midi_note // 12) - 1
        note = notes[midi_note % 12]
        return f"{note}{octave}"

if __name__ == "__main__":
    import pathlib
    output_dir = pathlib.Path(__file__).parent.resolve() / "../data/examples/transposition_exaples/" 
    generator = IntervalLikelihoodGenerator(output_dir)
    generator.generate_all_intervals(60)