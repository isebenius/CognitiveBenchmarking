from typing import Union
from pathlib import Path
import mido
import random


def transpose_midi(
    input_path: Union[str, Path], 
    output_path: Union[str, Path], 
    semitones: int = 0
) -> str:
    """Transpose a MIDI file by a specified number of semitones.
    
    Parameters
    ----------
    input_path : Union[str, Path]
        Path to the input MIDI file
    output_path : Union[str, Path], optional
        Path where the transposed MIDI file will be saved.
        If None, will use the input filename with a "_transposed_{semitones}" suffix.
    semitones : int, optional
        Number of semitones to transpose by (positive = up, negative = down)
        
    Returns
    -------
    str
        Path to the transposed MIDI file
    """

    # Convert paths to strings
    input_path = str(input_path)
    
    output_path = str(output_path)
    
    # Load the MIDI file
    midi_file = mido.MidiFile(input_path)
    
    # Create a new MIDI file with the same properties
    new_midi = mido.MidiFile(ticks_per_beat=midi_file.ticks_per_beat)
    
    # Process each track
    for track in midi_file.tracks:
        new_track = mido.MidiTrack()
        new_midi.tracks.append(new_track)
        
        # Process each message in the track
        for msg in track:
            # Copy the message
            new_msg = msg.copy()
            
            # Transpose note_on and note_off messages
            if msg.type == 'note_on' or msg.type == 'note_off':
                # Calculate the new note value
                new_note = msg.note + semitones
                
                # Ensure the note is within valid MIDI range (0-127)
                if 0 <= new_note <= 127:
                    new_msg.note = new_note
                else:
                    # If outside range, adjust octave but keep the same pitch class
                    while new_note < 0:
                        new_note += 12
                    while new_note > 127:
                        new_note -= 12
                    new_msg.note = new_note
            
            # Add the message to the new track
            new_track.append(new_msg)
    
    # Save the transposed MIDI file
    new_midi.save(output_path)
    
    return output_path


def time_dilate_midi(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    scale_factor: float = 1.0
) -> str:
    """Scale the duration of all notes in a MIDI file.
    
    Parameters
    ----------
    input_path : Union[str, Path]
        Path to the input MIDI file
    output_path : Union[str, Path], optional
        Path where the time-scaled MIDI file will be saved.
        If None, will use the input filename with a "_scaled_{factor}" suffix.
    scale_factor : float, optional
        Factor to scale note durations by. Values < 1 shorten notes, values > 1 lengthen them.
        For example, 0.5 means half as long, 2.0 means twice as long.
        
    Returns
    -------
    str
        Path to the time-scaled MIDI file
    """
    import mido
    from collections import defaultdict
    
    # Convert paths to strings
    input_path = str(input_path)
    
    output_path = str(output_path)
    
    # Load the MIDI file
    midi_file = mido.MidiFile(input_path)
    
    # Create a new MIDI file with the same properties
    new_midi = mido.MidiFile(ticks_per_beat=midi_file.ticks_per_beat)
    
    # Process each track
    for track in midi_file.tracks:
        new_track = mido.MidiTrack()
        new_midi.tracks.append(new_track)
        
        # Need to keep track of when each note was turned on
        note_on_times = defaultdict(list)  # Maps note number to a list of (channel, absolute_time) tuples
        absolute_time = 0  # Keep track of absolute time
        
        # First pass: collect all note_on events with their absolute times
        temp_absolute_time = 0
        for msg in track:
            temp_absolute_time += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:  # Real note_on event
                note_on_times[msg.note].append((msg.channel, temp_absolute_time))
        
        # Process each message and adjust timing
        for msg in track:
            # Update absolute time
            absolute_time += msg.time
            
            # Make a copy of the message for the new track
            new_msg = msg.copy()
            
            # Scale the delta time for this message
            new_msg.time = int(msg.time * scale_factor)
            
            # If this is a note_off event or a note_on with velocity 0 (equivalent to note_off)
            if (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                # Find the corresponding note_on event
                if msg.note in note_on_times and note_on_times[msg.note]:
                    channel, note_on_time = note_on_times[msg.note][0]
                    
                    # Only adjust if this is for the same channel
                    if channel == msg.channel:
                        # Calculate the original duration
                        original_duration = absolute_time - note_on_time
                        
                        # Scale the duration
                        scaled_duration = int(original_duration * scale_factor)
                        
                        # Remove this note_on from tracking
                        note_on_times[msg.note].pop(0)
            
            # Add the message to the new track
            new_track.append(new_msg)
    
    # Save the time-scaled MIDI file
    new_midi.save(output_path)
    
    return output_path


# def transpose_track(midi_file_path, output_path, track_index, semitones):
#     """
#     Load a MIDI file and transpose a specific track by a given number of semitones.
    
#     Args:
#         midi_file_path (str): Path to input MIDI file
#         output_path (str): Path for output MIDI file
#         track_index (int): Index of track to transpose (0-based)
#         semitones (int): Number of semitones to transpose (positive = up, negative = down)
#     """
#     # Load the MIDI file
#     mid = mido.MidiFile(midi_file_path)
    
#     # Check if track index is valid
#     if track_index >= len(mid.tracks):
#         raise ValueError(f"Track index {track_index} out of range. File has {len(mid.tracks)} tracks.")
    
#     # Create a copy to avoid modifying the original
#     new_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
    
#     for i, track in enumerate(mid.tracks):
#         new_track = mido.MidiTrack()
        
#         for msg in track:
#             # Copy the message
#             new_msg = msg.copy()
            
#             # If this is the track to transpose and the message has a note
#             if i == track_index and hasattr(msg, 'note') and msg.type in ['note_on', 'note_off']:
#                 # Transpose the note, ensuring it stays within MIDI range (0-127)
#                 new_note = max(0, min(127, msg.note + semitones))
#                 new_msg.note = new_note
            
#             new_track.append(new_msg)
        
#         new_mid.tracks.append(new_track)
    
#     # Save the transposed MIDI file
#     new_mid.save(output_path)
#     print(f"Transposed track {track_index} by {semitones} semitones. Saved to {output_path}")

# def reshuffle_bars(midi_file_path, output_path, ticks_per_bar=None, verbose = False):
#     """
#     Reshuffle the bars/segments of a MIDI file randomly.
    
#     Args:
#         midi_file_path (str): Path to input MIDI file
#         output_path (str): Path for output MIDI file
#         ticks_per_bar (int): Number of ticks per bar. If None, will estimate based on time signature
#     """
#     # Load the MIDI file
#     mid = mido.MidiFile(midi_file_path)
    
#     # If ticks_per_bar not provided, estimate it
#     if ticks_per_bar is None:
#         # Default assumption: 4/4 time signature
#         ticks_per_bar = mid.ticks_per_beat * 4
    
#     # Find the total length of the MIDI file
#     total_ticks = 0
#     for track in mid.tracks:
#         track_ticks = sum(msg.time for msg in track)
#         total_ticks = max(total_ticks, track_ticks)
    
#     # Calculate number of complete bars
#     num_bars = total_ticks // ticks_per_bar
#     if num_bars < 2:
#         print("Warning: MIDI file appears to have less than 2 complete bars. Shuffling may not be meaningful.")
    
#     if verbose:
#         print(f"Detected {num_bars} bars of {ticks_per_bar} ticks each")
    
#     # Create shuffled bar order
#     bar_order = list(range(num_bars))
#     random.shuffle(bar_order)
#     if verbose:
#         print(f"New bar order: {bar_order}")
    
#     # Create new MIDI file
#     new_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
    
#     # Process each track
#     for track in mid.tracks:
#         new_track = mido.MidiTrack()
        
#         # Split track into bars
#         bars = [[] for _ in range(num_bars)]
#         current_bar = 0
#         current_tick = 0
        
#         for msg in track:
#             # Add message to current bar
#             bars[current_bar].append(msg.copy())
            
#             # Update tick position
#             current_tick += msg.time
#             new_bar = current_tick // ticks_per_bar
            
#             # If we've moved to a new bar, adjust timing
#             if new_bar > current_bar and new_bar < num_bars:
#                 # Adjust the last message's timing to end exactly at bar boundary
#                 if bars[current_bar]:
#                     excess_time = current_tick - (new_bar * ticks_per_bar)
#                     bars[current_bar][-1].time -= excess_time
                    
#                     # Start next bar with the excess time
#                     current_bar = new_bar
#                     if excess_time > 0:
#                         # Create a new message with the excess time
#                         new_msg = msg.copy()
#                         new_msg.time = excess_time
#                         bars[current_bar].append(new_msg)
#                 else:
#                     current_bar = new_bar
        
#         # Rebuild track in shuffled order
#         for bar_idx in bar_order:
#             if bar_idx < len(bars):
#                 for msg in bars[bar_idx]:
#                     new_track.append(msg)
        
#         new_mid.tracks.append(new_track)
    
#     # Save the shuffled MIDI file
#     new_mid.save(output_path)

#     if verbose:
#         print(f"Reshuffled bars saved to {output_path}")
#     return output_path