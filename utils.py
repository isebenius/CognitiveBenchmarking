from typing import Union
from pathlib import Path
import mido

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

