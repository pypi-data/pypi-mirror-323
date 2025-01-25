#!/bin/bash

# Scan for .kicad_pro files
files=(*.kicad_pro)

# If no files found
if [ ${#files[@]} -eq 0 ]; then
    echo "No .kicad_pro files found in the current directory."
    exit 1
fi

# If only one file found, open it directly
if [ ${#files[@]} -eq 1 ]; then
    echo "Opening the only .kicad_pro file found: ${files[0]}"
    xdg-open "${files[0]}" &
else
    # If multiple files found, ask which one to open
    echo "Multiple .kicad_pro files found:"
    for i in "${!files[@]}"; do
        echo "$((i+1)). ${files[$i]}"
    done
    read -p "Enter the number of the file you want to open: " choice

    # Validate the user's choice
    if [[ ! $choice =~ ^[0-9]+$ ]] || [ $choice -lt 1 ] || [ $choice -gt ${#files[@]} ]; then
        echo "Invalid choice."
        exit 1
    fi

    # Open the selected file
    echo "Opening: ${files[$((choice-1))]}"
    xdg-open "${files[$((choice-1))]}" &
fi

# Wait 5 seconds before launching the Python module
echo "Waiting for 5 seconds before launching the Python module..."
sleep 5

# Run the Python command in the background
python -m kicad_auto_lib &

# Prompt the user to press Enter to exit
read -p "Press Enter to exit..."