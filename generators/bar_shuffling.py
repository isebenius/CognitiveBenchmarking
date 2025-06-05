"""
This script generates shuffled versions of MIDI files by randomly reordering their bars.
"""

from pathlib import Path
from typing import Union, Optional
import random

from .base_generator import MIDIGenerator
from ..utils import reshuffle_bars

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
    
    def generate_shuffled_versions(
        self,
        input_midi_path: Union[str, Path],
        num_versions: int = 5,
        ticks_per_bar: Optional[int] = None,
        random_seed: Optional[int] = None,
        verbose: bool = False
    ) -> list[str]:
        """Generate multiple shuffled versions of an input MIDI file.
        
        Parameters
        ----------
        input_midi_path : Union[str, Path]
            Path to the input MIDI file
        num_versions : int, optional
            Number of shuffled versions to generate, by default 5
        ticks_per_bar : Optional[int], optional
            Number of ticks per bar. If None, will estimate based on time signature, by default None
        random_seed : Optional[int], optional
            Seed for random number generation. If provided, ensures reproducible shuffling, by default None
        verbose : bool, optional
            Whether to print progress information, by default False
            
        Returns
        -------
        list[str]
            List of paths to the generated MIDI files
        """
        input_path = Path(input_midi_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input MIDI file not found: {input_path}")
        
        # Set random seed if provided
        if random_seed is not None:
            random.seed(random_seed)
        
        # Generate multiple shuffled versions
        output_paths = []
        for i in range(num_versions):
            # Create output filename with version number
            output_filename = f"{input_path.stem}_shuffled_v{i+1}{input_path.suffix}"
            output_path = self.output_dir / output_filename
            
            # Generate shuffled version
            reshuffle_bars(
                midi_file_path=str(input_path),
                output_path=str(output_path),
                ticks_per_bar=ticks_per_bar,
                verbose=verbose
            )
            
            output_paths.append(str(output_path))
            
            if verbose:
                print(f"Generated shuffled version {i+1}/{num_versions}: {output_path}")
        
        return output_paths

# if __name__ == "__main__":
#     # Example usage
#     import pathlib
#     output_dir = pathlib.Path(__file__).parent.resolve() / "../data/examples/bar_shuffling_examples"
#     generator = BarShufflingGenerator(output_dir)
    
    # Example: Generate 3 shuffled versions of a MIDI file with a fixed random seed
    # generator.generate_shuffled_versions(
    #     input_midi_path="path/to/input.mid",
    #     num_versions=3,
    #     random_seed=42,
    #     verbose=True
    # )
