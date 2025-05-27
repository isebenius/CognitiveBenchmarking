"""
This script generates stimuli of all possible continuations of a given melody.
It then saves the generated MIDI files to the output directory.
"""

from pathlib import Path
import mido
from .base_generator import MIDIGenerator

class MelodyContinuationGenerator(MIDIGenerator):
    """Generate all possible single-note continuations of a given melody."""
    
    def __init__(self, output_dir="continuation_examples"):
        """Initialize the generator."""
        super().__init__(output_dir)
        
        # Note names to MIDI numbers
        self.note_to_midi = {
            "C4": 60,
            "F#4": 66
        }
        
        # Notes dictionary for human-readable names
        self.notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    def generate_continuations(self, context_midi_path, context_end_note="C4", output_prefix=None, last_note_duration=480):
        """Generate continuation files for all possible next notes.
        
        Parameters
        ----------
        context_midi_path : str or Path
            Path to the MIDI file containing the context melody
        context_end_note : str
            The ending note of the context, either "C4" or "F#4"
        output_prefix : str, optional
            Prefix for output filenames. If None, uses the input filename
        last_note_duration : int, optional
            Duration in ticks for the continuation note
            
        Returns
        -------
        dict
            Maps index (1-25) to paths of generated files
        """
        # Validate ending note
        if context_end_note not in ["C4", "F#4"]:
            raise ValueError("context_end_note must be either 'C4' or 'F#4'")
        
        # Convert path to Path object
        context_path = Path(context_midi_path)
        
        # Load the context MIDI file
        try:
            context_midi = mido.MidiFile(context_path)
        except Exception as e:
            raise ValueError(f"Error reading MIDI file: {str(e)}")
        
        # Get output prefix from input filename if not provided
        if output_prefix is None:
            output_prefix = context_path.stem
        
        # Extract all messages from the context MIDI file
        context_messages = []
        for track in context_midi.tracks:
            for msg in track:
                # Make a copy to avoid modifying original
                if isinstance(msg, mido.Message):
                    context_messages.append(msg.copy())
                else:
                    context_messages.append(msg)
        
        # Find the last note_on message in the context
        last_note = None
        for msg in reversed(context_messages):
            if isinstance(msg, mido.Message) and msg.type == 'note_on' and msg.velocity > 0:
                last_note = msg.note
                break
        
        # Convert context_end_note to MIDI note number
        expected_note = None
        if context_end_note == "C4":
            expected_note = 60  # MIDI note number for C4
        elif context_end_note == "F#4":
            expected_note = 66  # MIDI note number for F#4
        
        # Validate that the last note matches what was specified
        if last_note != expected_note:
            raise ValueError(f"Context melody does not end on {context_end_note}. "
                           f"Found MIDI note {last_note} instead of {expected_note}")
        
        # Determine the pitch range based on the context ending note
        if context_end_note == "C4":
            base_note = 48  # C3
            top_note = 73   # C5 (exclusive)
            base_name = "C"
        else:  # F#4
            base_note = 54  # F#3
            top_note = 79   # F#5 (exclusive)
            base_name = "F#"
        
        # Generate a continuation for each of the 25 notes in the range
        continuations = {}
        
        for i, note in enumerate(range(base_note, top_note), 1):
            # Generate a new MIDI file with this continuation
            output_path = self._create_continuation(
                context_messages=context_messages,
                continuation_note=note,
                duration=last_note_duration,
                ticks_per_beat=context_midi.ticks_per_beat,
                output_prefix=output_prefix,
                index=i,
                context_end_note=context_end_note
            )
            
            continuations[i] = output_path
            
        return continuations
    
    def _create_continuation(self, context_messages, continuation_note, duration, 
                            ticks_per_beat, output_prefix, index, context_end_note):
        """Create a new MIDI file with the context plus a continuation note.
        
        Parameters
        ----------
        context_messages : list
            Messages from the context MIDI file
        continuation_note : int
            MIDI note number for the continuation
        duration : int
            Duration of the continuation note in ticks
        ticks_per_beat : int
            Ticks per beat for the MIDI file
        output_prefix : str
            Prefix for the output filename
        index : int
            Index number (1-25) for the note in the range
        context_end_note : str
            The ending note of the context ("C4" or "F#4")
            
        Returns
        -------
        str
            Path to the generated file
        """
        # Create a new MIDI file
        mid = self._create_midi_file(ticks_per_beat)
        track = mid.tracks[0]
        
        # Add all messages from context
        for msg in context_messages:
            track.append(msg)
        
        # Get a note name for the filename
        note_name = self._get_note_name(continuation_note)
        
        # Add continuation note
        self._add_note(track, continuation_note, velocity=90, time=0, duration=duration)
        
        # Create a filename - include context end note and index
        filename = f"{output_prefix}_from_{context_end_note}_cont_{index}_{note_name}.mid"
        return self._save_midi_file(mid, filename)
    
    def _get_note_name(self, midi_note):
        """Get a human-readable note name from MIDI note number."""
        octave = (midi_note // 12) - 1
        note = self.notes[midi_note % 12]
        return f"{note}{octave}"
    

if __name__ == "__main__":
    import pathlib
    output_dir = pathlib.Path(__file__).parent.resolve() / "/data/examples/ContinuationExamples" 
    generator = MelodyContinuationGenerator(output_dir)
    context_path = pathlib.Path(__file__).parent.resolve() / "/data/human_data/Stimuli/t_01/C4/M2_a.mid"
    generator.generate_continuations(context_path, "C4")