from pathlib import Path
from typing import Union, List, Dict, Optional
import random
import mido
from .base_generator import MIDIGenerator

class RandomNoteAlterationGenerator(MIDIGenerator):
    """Generate altered versions of a MIDI file by randomly shifting a specified number of notes by a given interval."""
    def __init__(self, output_dir: str = "note_alteration_examples"):
        super().__init__(output_dir)

    def generate_altered_versions(
        self,
        input_midi_path: Union[str, Path],
        num_versions: int = 5,
        notes_to_alter: int = 1,
        interval: int = 1,
        random_seed: Optional[int] = None,
        verbose: bool = False
    ) -> Dict[str, List[str]]:
        """
        Generate multiple altered versions of a MIDI file, each with a specified number of random notes shifted by a given interval.

        Parameters
        ----------
        input_midi_path : Union[str, Path]
            Path to the input MIDI file
        num_versions : int, optional
            Number of altered versions to generate, by default 5
        notes_to_alter : int, optional
            Number of notes to alter in each version, by default 1
        interval : int, optional
            Number of semitones to shift each altered note, by default 1 (half step up)
        random_seed : Optional[int], optional
            Seed for random number generation, by default None
        verbose : bool, optional
            Whether to print progress information, by default False

        Returns
        -------
        Dict[str, List[str]]
            Dictionary with a single key 'paths' containing a list of all generated file paths
        """
        input_path = Path(input_midi_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input MIDI file not found: {input_path}")

        if random_seed is not None:
            random.seed(random_seed)

        output_paths = []
        for i in range(num_versions):
            # Load the MIDI file fresh for each version
            midi_file = mido.MidiFile(str(input_path))
            # Collect all note_on events (track_idx, msg_idx, msg)
            note_events = []
            for track_idx, track in enumerate(midi_file.tracks):
                abs_time = 0
                for msg_idx, msg in enumerate(track):
                    abs_time += msg.time
                    if msg.type == 'note_on' and msg.velocity > 0:
                        note_events.append((track_idx, msg_idx, abs_time, msg))
            if len(note_events) < notes_to_alter:
                raise ValueError(f"Not enough notes in the file to alter {notes_to_alter} notes.")
            # Randomly select notes to alter
            selected_indices = random.sample(range(len(note_events)), notes_to_alter)
            selected_notes = [note_events[idx] for idx in selected_indices]
            # Alter the selected notes
            for track_idx, msg_idx, abs_time, msg in selected_notes:
                orig_note = msg.note
                new_note = max(0, min(127, orig_note + interval))
                midi_file.tracks[track_idx][msg_idx].note = new_note
                if verbose:
                    print(f"Altered note at track {track_idx}, index {msg_idx}, time {abs_time}: {orig_note} -> {new_note}")
                # Also update the corresponding note_off (or note_on with velocity 0)
                # Find the matching note_off in the same track, after this note_on
                track = midi_file.tracks[track_idx]
                for follow_idx in range(msg_idx + 1, len(track)):
                    follow_msg = track[follow_idx]
                    if (
                        (follow_msg.type == 'note_off' or (follow_msg.type == 'note_on' and follow_msg.velocity == 0))
                        and follow_msg.note == orig_note
                        and getattr(follow_msg, 'channel', getattr(msg, 'channel', 0)) == getattr(msg, 'channel', 0)
                    ):
                        track[follow_idx].note = new_note
                        if verbose:
                            print(f"  -> Updated corresponding note_off at index {follow_idx}: {orig_note} -> {new_note}")
                        break  # Only update the first matching note_off
            # Save the altered MIDI file
            output_filename = f"{input_path.stem}_altered_{notes_to_alter}notes_{interval:+}st_v{i+1}{input_path.suffix}"
            output_path = self.output_dir / output_filename
            midi_file.save(str(output_path))
            output_paths.append(str(output_path))
            if verbose:
                print(f"Saved altered version {i+1}/{num_versions}: {output_path}")
        return {"paths": output_paths}

# Example usage:
# generator = RandomNoteAlterationGenerator(output_dir="path/to/output")
# result = generator.generate_altered_versions(
#     input_midi_path="path/to/input.mid",
#     num_versions=10,
#     notes_to_alter=2,
#     interval=1,
#     random_seed=42,
#     verbose=True
# )
# # Access all paths: result["paths"] 