#!/usr/bin/env python3
"""
Concatenate 3 video clips into a single 15s video using ffmpeg.
Usage: python3 agnes-video-stitch.py <style_name> <clip1> <clip2> <clip3> <output>
"""
import sys, os, subprocess

def stitch(style, clips, output):
    for c in clips:
        if not os.path.exists(c) or os.path.getsize(c) < 100000:
            print(f"WARNING: {c} missing or too small")
    
    cmd = ["ffmpeg", "-y"]
    for c in clips:
        cmd.extend(["-i", c])
    filter_parts = ",".join([f"[{i}:v][{i}:a]" for i in range(len(clips))])
    cmd.extend([
        "-filter_complex", f"{filter_parts}concat=n={len(clips)}:v=1:a=1[outv][outa]",
        "-map", "[outv]", "-map", "[outa]",
        "-c:v", "libx264", "-c:a", "aac",
        output
    ])
    
    print(f"Stitching {style}: {' + '.join(clips)} -> {output}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ffmpeg stderr: {result.stderr[:300]}")
        # Fallback: video-only
        cmd2 = ["ffmpeg", "-y"]
        for c in clips:
            cmd2.extend(["-i", c])
        inputs = " ".join([f"[{i}:v]" for i in range(len(clips))])
        cmd2.extend(["-filter_complex", f"{inputs}concat=n={len(clips)}:v=1:a=0[outv]", "-map", "[outv]", output])
        result2 = subprocess.run(cmd2, capture_output=True, text=True)
        if result2.returncode != 0:
            print(f"Video-only also failed: {result2.stderr[:300]}")
            return False
    print(f"Done: {output} ({os.path.getsize(output)//1024}KB)")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print(__doc__)
        sys.exit(1)
    stitch(sys.argv[1], sys.argv[2:5], sys.argv[5])
