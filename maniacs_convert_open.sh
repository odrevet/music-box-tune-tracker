mid=$1
speed=$2
fpr="${mid%.*}".fpr
python3 maniacs_mid_to_fpr.py --speed-ratio=$speed --mid=$mid && python3 music_box_tracker.py --fpr=$fpr --port="TiMidity port 0"
