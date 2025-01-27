import os
import ffmpeg
from pathlib import Path
from typing import List, Tuple

class VideoProcessor:
    def __init__(self, input_dir: str):
        self.input_dir = Path(input_dir)
        
    def get_video_info(self, video_path: Path) -> tuple:
        probe = ffmpeg.probe(str(video_path))
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        
        # Get duration in minutes (rounded)
        duration_mins = round(float(probe['format']['duration']) / 60)
        
        # Get resolution
        width = int(video_info['width'])
        height = int(video_info['height'])
        resolution = f"{width}x{height}"
        pixels = width * height  # For sorting
        
        return duration_mins, resolution, pixels
    
    def get_sorted_videos(self) -> List[Tuple[Path, int, str, int]]:
        mp4_files = list(self.input_dir.glob('**/*.mp4'))
        video_info_list = []
        
        # Collect info for all videos
        for video_path in mp4_files:
            try:
                duration_mins, resolution, pixels = self.get_video_info(video_path)
                video_info_list.append((video_path, duration_mins, resolution, pixels))
            except Exception as e:
                print(f"Error processing {video_path.name}: {str(e)}")
                
        # Sort by duration and resolution (pixels), both in descending order
        return sorted(video_info_list, key=lambda x: (x[1], x[3]), reverse=True)
    
    def process_videos(self):
        sorted_videos = self.get_sorted_videos()
        
        # Keep track of used filenames to handle duplicates
        used_names = set()
        
        # Rename files with index based on sort order
        for index, (video_path, duration_mins, resolution, _) in enumerate(sorted_videos, 1):
            try:
                # Create base filename with index
                base_name = f"{index}_{duration_mins}_{resolution}"
                new_name = f"{base_name}.mp4"
                new_path = video_path.parent / new_name
                
                # Handle duplicates by adding a suffix
                suffix = 1
                while new_path in used_names or new_path.exists():
                    new_name = f"{base_name}_({suffix}).mp4"
                    new_path = video_path.parent / new_name
                    suffix += 1
                
                # Add to used names set
                used_names.add(new_path)
                
                # Rename file
                video_path.rename(new_path)
                print(f"Renamed: {video_path.name} -> {new_name}")
                
            except Exception as e:
                print(f"Error renaming {video_path.name}: {str(e)}")

def main():
    """Main entry point for the vid-mng application."""
    input_dir = input("Please enter the input directory path: ").strip()
    
    if not os.path.isdir(input_dir):
        print("Error: Invalid directory path")
        return
    
    processor = VideoProcessor(input_dir)
    processor.process_videos()

if __name__ == "__main__":
    main()
