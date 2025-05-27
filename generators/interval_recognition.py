"""
This script generates stimuli for interval recognition.
It generates context examples of a given interval, then generates all possible endings for the interval based on a test note note seen before.
It then saves the generated MIDI files to the output directory.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import mido
import random
from .base_generator import MIDIGenerator

class IntervalRecognitionGenerator(MIDIGenerator):
    """Generator for interval recognition test examples with comprehensive test cases."""
    
    def __init__(self, output_dir="interval_examples"):
        """Initialize with intervals from -12 to +12 semitones."""
        super().__init__(output_dir)
        
        # Define intervals from -12 to +12 semitones (octave below to octave above)
        self.intervals = {}
        
        # Negative intervals (going down)
        self.intervals["-octave"] = -12
        self.intervals["-maj7"] = -11
        self.intervals["-min7"] = -10
        self.intervals["-maj6"] = -9
        self.intervals["-min6"] = -8
        self.intervals["-p5"] = -7
        self.intervals["-tritone"] = -6
        self.intervals["-p4"] = -5
        self.intervals["-maj3"] = -4
        self.intervals["-min3"] = -3
        self.intervals["-maj2"] = -2
        self.intervals["-min2"] = -1
        
        # Unison
        self.intervals["unison"] = 0
        
        # Positive intervals (going up)
        self.intervals["min2"] = 1
        self.intervals["maj2"] = 2
        self.intervals["min3"] = 3
        self.intervals["maj3"] = 4
        self.intervals["p4"] = 5
        self.intervals["tritone"] = 6
        self.intervals["p5"] = 7
        self.intervals["min6"] = 8
        self.intervals["maj6"] = 9
        self.intervals["min7"] = 10
        self.intervals["maj7"] = 11
        self.intervals["octave"] = 12
        
        # Note range for examples (C3-C5)
        self.note_range = list(range(48, 73))  # C3(48) to C5(72)
    
    def generate_comprehensive_test(self, interval_name, num_examples=4):
        """Generate MIDI files for a target interval with all possible endings.
        
        Parameters
        ----------
        interval_name : str
            Name of interval to test (must be in self.intervals)
        num_examples : int
            Number of example intervals to include before test
            
        Returns
        -------
        dict
            Paths to generated files {"target": path, "interval_name": path, ...}
        """
        target_interval = self.intervals[interval_name]
        
        # Select random notes from C3-C5 range for examples
        available_notes = self.note_range.copy()
        random.shuffle(available_notes)
        
        # Get starting notes for context examples
        context_start_notes = available_notes[:num_examples]
        
        # Create list of all notes that were used in the context (both start and end notes)
        used_notes = context_start_notes.copy()
        for start_note in context_start_notes:
            end_note = start_note + target_interval
            # Ensure end note is in valid MIDI range (0-127)
            if 0 <= end_note <= 127:
                used_notes.append(end_note)
        
        # Find a note that hasn't been used for the test case, and if all are used, pick a random one
        possible_test_start_notes = [note for note in available_notes if note not in used_notes]
        if len(possible_test_start_notes) > 0:
            test_start_note = random.choice(possible_test_start_notes)
        else:
            raise ValueError(f"No notes available for test case for interval {interval_name}")
        
        # Generate all possible interval endings
        results = {}
        
        for test_interval_name, test_interval in self.intervals.items():
            # Calculate the test ending note
            test_end_note = test_start_note + test_interval
            
            # Skip if test end note is outside MIDI range
            if not (0 <= test_end_note <= 127):
                continue
            
            # Mark if this is the target interval
            is_target = (test_interval == target_interval)
            
            # Generate MIDI file
            output_path = self._create_midi(
                target_name=interval_name,
                target_interval=target_interval,
                context_notes=context_start_notes,
                test_note=test_start_note,
                test_interval=test_interval,
                is_target=is_target,
                test_name=test_interval_name
            )
            
            # Store the result
            results[test_interval_name] = output_path
        
        return results
    
    def _create_midi(self, target_name, target_interval, context_notes, 
                    test_note, test_interval, is_target, test_name):
        """Create a MIDI file with interval examples and test case."""
        # Create MIDI file
        mid = self._create_midi_file()
        track = mid.tracks[0]
        
        # Add context examples
        for i, start_note in enumerate(context_notes):
            # First note
            first_delay = 0 if i == 0 else 480  # Longer delay for first example
            self._add_note(track, start_note, velocity=80, time=first_delay, duration=480)
            
            # Second note (target interval)
            end_note = start_note + target_interval
            # Skip this example if end note is outside MIDI range
            if not (0 <= end_note <= 127):
                continue
                
            self._add_note(track, end_note, velocity=80, time=0, duration=480)

        
        # Test case: first note. Includes pause
        self._add_note(track, test_note, velocity=90, time=480, duration=480)
        
        # Test case: second note (target or other interval)
        test_end = test_note + test_interval
        self._add_note(track, test_end, velocity=90, time=0, duration=480)
        
        # Create filename
        if is_target:
            filename = f"{target_name}_correct.mid"
        else:
            filename = f"{target_name}_test_{test_name}.mid"
            
        return self._save_midi_file(mid, filename)

if __name__ == "__main__":
    import pathlib
    output_dir = pathlib.Path(__file__).parent.resolve() / "../data/examples/IntervalExamples" 
    generator = IntervalRecognitionGenerator(output_dir)
    generator.generate_comprehensive_test("p4", num_examples=10)