#!/usr/bin/env python3
"""
Video Creation Examples for Street View Hyperlapse

This script demonstrates different Python libraries for creating videos from frame sequences.
Each method has different advantages for different use cases.
"""

import cv2
import numpy as np
from pathlib import Path
import glob
from PIL import Image

# Example 1: OpenCV (cv2) - Most Popular and Fast
def create_video_opencv(frame_dir, output_path, fps=2):
    """
    Create video using OpenCV - fastest and most reliable method.
    
    Args:
        frame_dir (str): Directory containing frame images
        output_path (str): Output video file path
        fps (int): Frames per second
    """
    print("🎬 Creating video with OpenCV...")
    
    # Get all PNG files sorted by name
    frame_files = sorted(glob.glob(str(Path(frame_dir) / "*.png")))
    
    if not frame_files:
        print("❌ No PNG files found!")
        return
    
    # Read first frame to get dimensions
    first_frame = cv2.imread(frame_files[0])
    height, width, layers = first_frame.shape
    
    # Define codec and create VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can also use 'XVID'
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"📊 Processing {len(frame_files)} frames at {fps} FPS...")
    
    for i, frame_file in enumerate(frame_files):
        frame = cv2.imread(frame_file)
        video_writer.write(frame)
        
        if (i + 1) % 5 == 0:
            print(f"✅ Processed {i + 1}/{len(frame_files)} frames")
    
    video_writer.release()
    print(f"🎉 Video created: {output_path}")


# Example 2: MoviePy - High-Level and Feature-Rich
def create_video_moviepy(frame_dir, output_path, fps=2):
    """
    Create video using MoviePy - great for effects and editing.
    
    Note: Requires installation: pip install moviepy
    """
    try:
        from moviepy.editor import ImageSequenceClip
        
        print("🎭 Creating video with MoviePy...")
        
        # Get frame files
        frame_files = sorted(glob.glob(str(Path(frame_dir) / "*.png")))
        
        if not frame_files:
            print("❌ No PNG files found!")
            return
        
        # Create clip from image sequence
        clip = ImageSequenceClip(frame_files, fps=fps)
        
        # Write video file
        clip.write_videofile(
            output_path,
            codec='libx264',
            audio=False,
            verbose=False,
            logger=None  # Suppress verbose output
        )
        
        print(f"🎉 Video created: {output_path}")
        
    except ImportError:
        print("⚠️ MoviePy not installed. Install with: pip install moviepy")


# Example 3: imageio - Simple and Lightweight
def create_video_imageio(frame_dir, output_path, fps=2):
    """
    Create video using imageio - simple and lightweight.
    
    Note: Requires installation: pip install imageio[ffmpeg]
    """
    try:
        import imageio
        
        print("📷 Creating video with imageio...")
        
        # Get frame files
        frame_files = sorted(glob.glob(str(Path(frame_dir) / "*.png")))
        
        if not frame_files:
            print("❌ No PNG files found!")
            return
        
        # Create writer
        writer = imageio.get_writer(output_path, fps=fps)
        
        for frame_file in frame_files:
            image = imageio.imread(frame_file)
            writer.append_data(image)
        
        writer.close()
        print(f"🎉 Video created: {output_path}")
        
    except ImportError:
        print("⚠️ imageio not installed. Install with: pip install imageio[ffmpeg]")


# Example 4: Advanced OpenCV with Effects
def create_video_opencv_advanced(frame_dir, output_path, fps=2):
    """
    Create video with OpenCV including transition effects and better encoding.
    """
    print("🎨 Creating advanced video with OpenCV...")
    
    frame_files = sorted(glob.glob(str(Path(frame_dir) / "*.png")))
    
    if not frame_files:
        print("❌ No PNG files found!")
        return
    
    # Read first frame for dimensions
    first_frame = cv2.imread(frame_files[0])
    height, width, layers = first_frame.shape
    
    # Use H.264 codec for better compression
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for i, frame_file in enumerate(frame_files):
        frame = cv2.imread(frame_file)
        
        # Optional: Add fade effect between frames
        if i > 0:
            # Simple crossfade effect (can be customized)
            alpha = 0.8  # Adjust for fade strength
            frame = cv2.addWeighted(frame, alpha, frame, 1-alpha, 0)
        
        # Optional: Add text overlay
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f'Frame {i+1}', (50, 50), font, 1, (255, 255, 255), 2)
        
        video_writer.write(frame)
    
    video_writer.release()
    print(f"🎉 Enhanced video created: {output_path}")


# Example 5: Create GIF Animation
def create_gif_pillow(frame_dir, output_path, duration=500):
    """
    Create animated GIF using Pillow.
    
    Args:
        frame_dir (str): Directory containing frames
        output_path (str): Output GIF path  
        duration (int): Duration per frame in milliseconds
    """
    print("🎞️ Creating animated GIF...")
    
    frame_files = sorted(glob.glob(str(Path(frame_dir) / "*.png")))
    
    if not frame_files:
        print("❌ No PNG files found!")
        return
    
    # Load images
    images = []
    for frame_file in frame_files:
        img = Image.open(frame_file)
        # Resize for smaller GIF if needed
        img = img.resize((img.width // 2, img.height // 2), Image.Resampling.LANCZOS)
        images.append(img)
    
    # Save as animated GIF
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0  # Infinite loop
    )
    
    print(f"🎉 Animated GIF created: {output_path}")


# Main demonstration function
def main():
    """Demonstrate different video creation methods."""
    
    # Configuration
    frame_directory = "frames"  # Directory with your captured frames
    output_directory = "videos"
    
    # Create output directory
    Path(output_directory).mkdir(exist_ok=True)
    
    print("🎬 Video Creation Examples")
    print("=" * 50)
    
    # Check if frame directory exists
    if not Path(frame_directory).exists():
        print(f"⚠️ Frame directory '{frame_directory}' not found.")
        print("   Run the hyperlapse capture first!")
        return
    
    # Method 1: OpenCV (Recommended for most cases)
    create_video_opencv(
        frame_directory,
        f"{output_directory}/hyperlapse_opencv.mp4",
        fps=2
    )
    
    # Method 2: MoviePy (Best for effects)
    create_video_moviepy(
        frame_directory,
        f"{output_directory}/hyperlapse_moviepy.mp4", 
        fps=2
    )
    
    # Method 3: imageio (Simple)
    create_video_imageio(
        frame_directory,
        f"{output_directory}/hyperlapse_imageio.mp4",
        fps=2
    )
    
    # Method 4: Advanced OpenCV
    create_video_opencv_advanced(
        frame_directory,
        f"{output_directory}/hyperlapse_advanced.mp4",
        fps=2
    )
    
    # Method 5: Create GIF
    create_gif_pillow(
        frame_directory,
        f"{output_directory}/hyperlapse.gif",
        duration=500
    )
    
    print("\n🎉 All video creation methods demonstrated!")
    print(f"📁 Check the '{output_directory}' folder for results")


if __name__ == "__main__":
    main()
