"""
This script generates shuffled versions of MIDI files by randomly reordering their bars.
"""

from pathlib import Path
from typing import Union, Optional, Dict, List, Tuple
import random
import mido
from .base_generator import MIDIGenerator
import math

class BarShufflingGenerator(MIDIGenerator):
    """Generate shuffled versions of MIDI files by randomly reordering their bars."""
    
    def __init__(self, output_dir: str = "bar_shuffling_examples"):
        """Initialize the generator.
        
        Parameters
        ----------
        output_dir : str, optional
            Directory to save generated MIDI files, by default "bar_shuffling_examples"
        """
        super().__init__(output_dir)
    
    def _get_time_signature(self, midi_file: mido.MidiFile) -> Tuple[int, int]:
        """Extract time signature from MIDI file meta messages.
        
        Parameters
        ----------
        midi_file : mido.MidiFile
            The MIDI file to analyze
            
        Returns
        -------
        Tuple[int, int]
            Tuple of (numerator, denominator) representing the time signature
            
        Raises
        ------
        ValueError
            If no time signature is found in the MIDI file
        """
        for track in midi_file.tracks:
            for msg in track:
                if msg.type == 'time_signature':
                    return msg.numerator, msg.denominator
        
        raise ValueError("No time signature found in MIDI file. Time signature is required for bar shuffling.")
    
    def _calculate_ticks_per_bar(self, midi_file: mido.MidiFile, time_signature: Tuple[int, int]) -> int:
        """Calculate the number of ticks per bar based on time signature.
        
        Parameters
        ----------
        midi_file : mido.MidiFile
            The MIDI file
        time_signature : Tuple[int, int]
            Tuple of (numerator, denominator) representing the time signature
            
        Returns
        -------
        int
            Number of ticks per bar
        """
        numerator, denominator = time_signature
        # Calculate how many quarter notes are in a bar
        quarter_notes_per_bar = (numerator * 4) / denominator
        # Multiply by ticks per beat (which is ticks per quarter note)
        return int(quarter_notes_per_bar * midi_file.ticks_per_beat)
    
    def _calculate_possible_shuffles(self, num_phrases: int, preserve_first_and_last: bool) -> int:
        """Calculate the total number of possible unique shuffles.
        
        Parameters
        ----------
        num_phrases : int
            Number of phrases to shuffle
        preserve_first_and_last : bool
            Whether first and last phrases are preserved
            
        Returns
        -------
        int
            Number of possible unique shuffles
        """
        if preserve_first_and_last:
            # If preserving first and last, we only shuffle middle phrases
            if num_phrases <= 2:
                return 1  # Can't shuffle if only 2 or fewer phrases
            return math.factorial(num_phrases - 2)
        else:
            return math.factorial(num_phrases)

    def generate_shuffled_versions(
        self,
        input_midi_path: Union[str, Path],
        num_versions: int = 5,
        ticks_per_bar: Optional[int] = None,
        phrase_length: int = 1,
        random_seed: Optional[int] = None,
        preserve_first_and_last: bool = False,
        verbose: bool = False
    ) -> Dict[str, List[str]]:
        """Generate multiple shuffled versions of an input MIDI file.
        
        Parameters
        ----------
        input_midi_path : Union[str, Path]
            Path to the input MIDI file
        num_versions : int, optional
            Number of shuffled versions to generate, by default 5
        ticks_per_bar : Optional[int], optional
            Number of ticks per bar. If None, will calculate from time signature, by default None
        phrase_length : int, optional
            Number of consecutive bars to treat as a phrase for shuffling, by default 1
        random_seed : Optional[int], optional
            Seed for random number generation. If provided, ensures reproducible shuffling, by default None
        preserve_first_and_last : bool, optional
            Whether to keep the first and last phrases in their original positions, by default False
        verbose : bool, optional
            Whether to print progress information, by default False
            
        Returns
        -------
        Dict[str, List[str]]
            Dictionary with a single key 'paths' containing a list of all generated file paths
            
        Raises
        ------
        ValueError
            If no time signature is found in the MIDI file and ticks_per_bar is not provided
        """
        input_path = Path(input_midi_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input MIDI file not found: {input_path}")
        
        # Validate phrase_length
        if phrase_length < 1:
            raise ValueError("phrase_length must be at least 1")
        
        # Load MIDI file to get time signature
        midi_file = mido.MidiFile(str(input_path))
        
        # If ticks_per_bar not provided, calculate it from time signature
        if ticks_per_bar is None:
            time_signature = self._get_time_signature(midi_file)
            ticks_per_bar = self._calculate_ticks_per_bar(midi_file, time_signature)
            if verbose:
                print(f"Detected time signature: {time_signature[0]}/{time_signature[1]}")
                print(f"Calculated ticks per bar: {ticks_per_bar}")
        
        # Calculate effective ticks per shuffling unit (phrase)
        ticks_per_phrase = ticks_per_bar * phrase_length
        
        # Calculate total number of phrases
        total_ticks = 0
        for track in midi_file.tracks:
            track_ticks = sum(msg.time for msg in track)
            total_ticks = max(total_ticks, track_ticks)
        num_phrases = (total_ticks + ticks_per_phrase - 1) // ticks_per_phrase
        
        # Calculate possible unique shuffles
        possible_shuffles = self._calculate_possible_shuffles(num_phrases, preserve_first_and_last)
        
        if verbose:
            print(f"Total phrases: {num_phrases}")
            print(f"Possible unique shuffles: {possible_shuffles}")
        
        # Adjust num_versions if necessary
        if num_versions > possible_shuffles:
            print(f"Warning: Requested {num_versions} versions but only {possible_shuffles} unique shuffles possible. "
                  f"Returning {possible_shuffles} unique versions.")
            num_versions = possible_shuffles
        
        if verbose and phrase_length > 1:
            print(f"Shuffling phrases of {phrase_length} bars each ({ticks_per_phrase} ticks per phrase)")
        
        # Set random seed if provided
        if random_seed is not None:
            random.seed(random_seed)
        
        # Generate multiple shuffled versions
        output_paths = []
        used_orders = set()  # Track used shuffle orders to ensure uniqueness
        
        for i in range(num_versions):
            # Create output filename with version number
            phrase_suffix = f"_phrase{phrase_length}" if phrase_length > 1 else ""
            output_filename = f"{input_path.stem}_shuffled{phrase_suffix}_v{i+1}{input_path.suffix}"
            output_path = self.output_dir / output_filename
            
            # Generate shuffled version using phrase-sized units
            self._reshuffle_bars(
                midi_file_path=str(input_path),
                output_path=str(output_path),
                ticks_per_bar=ticks_per_phrase,  # Use phrase size as the shuffling unit
                verbose=verbose,
                preserve_first_and_last=preserve_first_and_last,
                used_orders=used_orders
            )
            
            output_paths.append(str(output_path))
            
            if verbose:
                print(f"Generated shuffled version {i+1}/{num_versions}: {output_path}")
        
        return {"paths": output_paths}
    
    def _reshuffle_bars(
        self,
        midi_file_path: str,
        output_path: str,
        ticks_per_bar: int,
        verbose: bool = False,
        preserve_first_and_last: bool = True,
        used_orders: Optional[set] = None
    ) -> str:
        """Reshuffle the bars/segments of a MIDI file randomly.
        
        Parameters
        ----------
        midi_file_path : str
            Path to input MIDI file
        output_path : str
            Path for output MIDI file
        ticks_per_bar : int
            Number of ticks per bar
        verbose : bool, optional
            Whether to print progress information, by default False
        preserve_first_and_last : bool, optional
            Whether to keep the first and last bars/phrases in their original positions, by default True
        used_orders : Optional[set], optional
            Set of previously used shuffle orders to avoid duplicates, by default None
            
        Returns
        -------
        str
            Path to the output file
        """
        # Load the MIDI file
        mid = mido.MidiFile(midi_file_path)
        
        # Find the total length of the MIDI file
        total_ticks = 0
        track_lengths = []
        for track in mid.tracks:
            track_ticks = sum(msg.time for msg in track)
            track_lengths.append(track_ticks)
            total_ticks = max(total_ticks, track_ticks)
        # Calculate number of bars (round up to include any partial bar)
        num_bars = (total_ticks + ticks_per_bar - 1) // ticks_per_bar
        if num_bars < 2:
            raise ValueError("MIDI file must have at least 2 complete bars for shuffling to be meaningful.")
        if verbose:
            print(f"Detected {num_bars} bars of {ticks_per_bar} ticks each")
        
        # Create shuffled bar order
        max_attempts = 100  # Prevent infinite loops
        attempts = 0
        while attempts < max_attempts:
            if preserve_first_and_last:
                # Create list of bars excluding first and last
                middle_bars = list(range(1, num_bars - 1))
                random.shuffle(middle_bars)
                # Construct final order with fixed first and last bars
                bar_order = [0] + middle_bars + [num_bars - 1]
            else:
                bar_order = list(range(num_bars))
                random.shuffle(bar_order)
            
            # Convert order to tuple for hashing
            order_tuple = tuple(bar_order)
            
            # If no used_orders set provided or this is a new order, proceed
            if used_orders is None or order_tuple not in used_orders:
                if used_orders is not None:
                    used_orders.add(order_tuple)
                break
            
            attempts += 1
            if attempts == max_attempts:
                raise ValueError("Could not generate a unique shuffle order after maximum attempts")
        
        if verbose:
            print(f"New bar order: {bar_order}")
        
        # Create new MIDI file
        new_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
        # Process each track
        for track in mid.tracks:
            # Step 1: Split into bars and collect meta messages
            bars = [[] for _ in range(num_bars)]  # Each bar: list of (msg, relative_time_in_bar, original_abs_time)
            meta_messages = []  # (msg, abs_time)
            active_notes = {}  # {(channel, note): (note_on_msg, note_on_abs_time, note_on_bar)}
            abs_time = 0
            for msg in track:
                abs_time += msg.time
                if msg.is_meta and msg.type != 'end_of_track':
                    meta_messages.append((msg.copy(), abs_time))
                else:
                    bar_idx = min(abs_time // ticks_per_bar, num_bars - 1)
                    relative_time_in_bar = abs_time - (bar_idx * ticks_per_bar)
                    
                    # Handle note events for cross-bar note splitting
                    if hasattr(msg, 'note') and hasattr(msg, 'channel'):
                        note_key = (msg.channel, msg.note)
                        
                        if msg.type == 'note_on' and msg.velocity > 0:
                            # Start of a note
                            active_notes[note_key] = (msg.copy(), abs_time, bar_idx)
                            bars[bar_idx].append((msg.copy(), relative_time_in_bar, abs_time))
                            
                        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                            # End of a note
                            if note_key in active_notes:
                                note_on_msg, note_on_time, note_on_bar = active_notes[note_key]
                                
                                if note_on_bar != bar_idx:
                                    # Note spans multiple bars - split it
                                    for span_bar in range(note_on_bar, bar_idx):
                                        # Add note_off at end of this bar
                                        note_off_time = (span_bar + 1) * ticks_per_bar
                                        note_off_rel_time = note_off_time - (span_bar * ticks_per_bar)
                                        note_off = mido.Message('note_off', note=msg.note, velocity=0, channel=msg.channel)
                                        bars[span_bar].append((note_off, note_off_rel_time, note_off_time))
                                        
                                        # Add note_on at start of next bar (if not the final bar)
                                        if span_bar + 1 < bar_idx:
                                            note_on_time_next = (span_bar + 1) * ticks_per_bar
                                            note_on_rel_time = 0
                                            note_on = mido.Message('note_on', note=msg.note, velocity=note_on_msg.velocity, channel=msg.channel)
                                            bars[span_bar + 1].append((note_on, note_on_rel_time, note_on_time_next))
                                
                                # Add the final note_off
                                bars[bar_idx].append((msg.copy(), relative_time_in_bar, abs_time))
                                del active_notes[note_key]
                            else:
                                # note_off without matching note_on
                                bars[bar_idx].append((msg.copy(), relative_time_in_bar, abs_time))
                        else:
                            # Other note messages
                            bars[bar_idx].append((msg.copy(), relative_time_in_bar, abs_time))
                    else:
                        # Non-note messages
                        bars[bar_idx].append((msg.copy(), relative_time_in_bar, abs_time))
            
            # Handle any remaining active notes (notes that never got note_off)
            for note_key, (note_on_msg, note_on_time, note_on_bar) in active_notes.items():
                # Add a note_off at the end of the track
                note_off = mido.Message('note_off', 
                                    channel=note_on_msg.channel, 
                                    note=note_on_msg.note, 
                                    velocity=64)
                # Put it in the last bar where the note started, at the end of the track
                final_rel_time = total_ticks - (note_on_bar * ticks_per_bar)
                bars[note_on_bar].append((note_off, final_rel_time, total_ticks))
            
            # Sort messages within each bar by relative time
            for bar in bars:
                bar.sort(key=lambda item: item[1])  # Sort by relative time in bar
            
            # Step 2: Rebuild track using shuffled bars
            all_msgs = []  # (msg, new_abs_time)
            current_abs_time = 0
            for shuffled_bar_pos, bar_idx in enumerate(bar_order):
                bar_start_time = shuffled_bar_pos * ticks_per_bar
                for msg, rel_time_in_bar, orig_abs_time in bars[bar_idx]:
                    new_abs_time = bar_start_time + rel_time_in_bar
                    all_msgs.append((msg, new_abs_time))
                # Always advance current_abs_time by ticks_per_bar
                current_abs_time = bar_start_time + ticks_per_bar
            # Step 3: Add meta messages at their original absolute time
            for meta_msg, meta_abs_time in meta_messages:
                all_msgs.append((meta_msg, meta_abs_time))
            # Step 4: Sort all messages by new absolute time
            all_msgs.sort(key=lambda item: item[1])
            # Step 5: Recalculate delta times and build the new track
            rebuilt_track = mido.MidiTrack()
            last_abs_time = 0
            for msg, abs_time in all_msgs:
                msg.time = abs_time - last_abs_time
                rebuilt_track.append(msg)
                last_abs_time = abs_time
            # Step 6: Ensure the last message is end_of_track
            if not (len(rebuilt_track) > 0 and rebuilt_track[-1].is_meta and rebuilt_track[-1].type == 'end_of_track'):
                from mido import MetaMessage
                rebuilt_track.append(mido.MetaMessage('end_of_track', time=0))
            new_mid.tracks.append(rebuilt_track)
        
        # Save the shuffled MIDI file
        new_mid.save(output_path)
        if verbose:
            print(f"Reshuffled bars saved to {output_path}")
        return output_path

# Example usage:
# generator = BarShufflingGenerator(output_dir="path/to/output")
# 
# # Shuffle individual bars (default behavior)
# result = generator.generate_shuffled_versions(
#     input_midi_path="path/to/input.mid",
#     num_versions=3,
#     random_seed=42,
#     verbose=True
# )
# 
# # Shuffle 4-bar phrases, preserving intro and outro
# result = generator.generate_shuffled_versions(
#     input_midi_path="path/to/input.mid",
#     num_versions=3,
#     phrase_length=4,
#     preserve_first_and_last=True,
#     random_seed=42,
#     verbose=True
# )
# 
# # Shuffle 8-bar phrases, shuffling everything including intro/outro
# result = generator.generate_shuffled_versions(
#     input_midi_path="path/to/input.mid",
#     num_versions=2,
#     phrase_length=8,
#     preserve_first_and_last=False,
#     random_seed=42,
#     verbose=True
# )
# 
# # Access all paths: result["paths"]


