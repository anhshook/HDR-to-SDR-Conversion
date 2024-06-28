import os
import shutil
import subprocess
from tqdm import tqdm


def convert_hdr_to_sdr(input_folder, output_folder):
    # Ensure absolute paths are used
    input_folder = os.path.abspath(input_folder)
    output_folder = os.path.abspath(output_folder)

    # Check if the input folder exists
    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"Input folder does not exist: 
{input_folder}")

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Supported video file extensions
    video_extensions = {".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv"}
    video_files = [f for f in os.listdir(input_folder) if 
any(f.lower().endswith(ext) for ext in video_extensions)]
    total_files = len(video_files)

    print("Conversion process started.")

    # Initialize progress bar
    with tqdm(total=total_files, desc="Converting videos", unit="file") as 
pbar:
        for i, filename in enumerate(video_files, 1):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # Construct the ffmpeg command
            command = [
                'ffmpeg',
                '-y',  # Always overwrite without prompting
                '-i', input_path,
                '-vf',
                
'zscale=t=linear:npl=100,format=gbrpf32le,tonemap=hable:desat=0,zscale=p=bt709:t=bt709:m=bt709,format=yuv420p',
                '-c:v', 'libx264',
                '-c:a', 'copy',
                output_path
            ]

            try:
                # Run the ffmpeg command and stream the output
                process = subprocess.Popen(command, 
stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                # Stream output to tqdm progress bar
                while True:
                    output = process.stderr.readline()
                    if process.poll() is not None:
                        break
                    if output:
                        print(output.strip())

                rc = process.poll()
                if rc != 0:
                    raise subprocess.CalledProcessError(rc, command)

                pbar.update(1)  # Update progress bar after each file
                print(f"Converted {i}/{total_files}: {filename}")
            except subprocess.CalledProcessError as e:
                print(f"Error converting {filename}: {e}")

    print("Conversion process completed.")


def organize_files(output_folder):
    files = [f for f in os.listdir(output_folder) if
             os.path.isfile(os.path.join(output_folder, f)) and not 
f.startswith('.')]

    prefix_dict = {}
    for filename in files:
        prefix = filename.split('-')[0].strip()
        if prefix not in prefix_dict:
            prefix_dict[prefix] = []
        prefix_dict[prefix].append(filename)

    for prefix, files in prefix_dict.items():
        # Only create folders for prefixes with multiple files
        if len(files) > 1:
            folder_path = os.path.join(output_folder, prefix)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            for filename in files:
                src_path = os.path.join(output_folder, filename)
                dst_path = os.path.join(folder_path, filename)
                shutil.move(src_path, dst_path)

    print("Files have been organized into folders.")


if __name__ == "__main__":
    input_folder = '/Users/anh/Downloads/Python code work/Color 
fixing/videos'
    output_folder = '/Users/anh/Downloads/Python code work/Color 
fixing/output_videos'

    # Convert HDR to SDR
    convert_hdr_to_sdr(input_folder, output_folder)

    # Ask if the user wants to organize the files
    organize = input("Do you want to organize the files into folders based 
on their names? (yes/no): ").strip().lower()
    if organize == 'yes':
        # Print the files before organizing
        print("Files before organizing:")
        print(os.listdir(output_folder))

        # Organize the files
        organize_files(output_folder)

        # Print the files after organizing
        print("Files after organizing:")
        for root, dirs, files in os.walk(output_folder):
            level = root.replace(output_folder, '').count(os.sep)
            indent = ' ' * 4 * (level)
            print('{}{}/'.format(indent, os.path.basename(root)))
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                print('{}{}'.format(subindent, f))

