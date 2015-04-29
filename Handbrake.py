#!/usr/bin/env python

##############################################################################
### NZBGET POST-PROCESSING SCRIPT                                          ###

# Process resulting videos with HandBrakeCLI
#
# This creates .json files in a queue directory with in and out paths to
# send to HandBrakeCLI. It will convert the video using one of the built
# in presets and output to an out directory.
#
# If the process is not already running, it will kick off the included
# handbraked script, which looks for unprocessed items in the queue. If
# no items remain unprocessed for some amount of time, it will quit until
# the next time it is started.

import os, sys, time, glob, subprocess

##############################################################################
### OPTIONS                                                                ###

# Queue directory
#
# Directory to store temporary .json files used to feed the handbraked script.
# These will be consumd one by one (marked .processing) and deleted after the
# conversion is complete.
#QueueDir=${DestDir}/_queue

# Output directory
#
# Processed files will end up here under the same relative paths as they were found
# in the input directory.
#OutDir=${DestDir}/_out

# Video extensions
#
# A comma separated list of video extensions to look for. Any video files in the
# directory will be processed if they have these extensions.
#VideoExtensions=.mkv,.avi,.divx,.xvid,.mov,.wmv,.mp4,.mpg,.mpeg,.vob,.iso

# HandBrakeCLI path
#
# Path to the HandBrakeCLI binary (must be downloaded separately)
#CLIPath=/usr/local/bin/HandBrakeCLI

# HandBrake preset
#
# One of the basic presets included in HandBrake to process with.
#Preset=Normal

# Output extension
#
# Extension to give the converted version of the file.
#OutputExtension=mp4

### NZBGET POST-PROCESSING SCRIPT                                          ###
##############################################################################

POSTPROCESS_SUCCESS=93
POSTPROCESS_NONE=95
POSTPROCESS_ERROR=94

current_script_dir = os.path.dirname(os.path.realpath(__file__))

print('[INFO] Handbrake post processing: %s' % os.environ['NZBPP_FINALDIR'])

queue_dir=os.environ['NZBPO_QUEUEDIR']
out_dir=os.environ['NZBPO_OUTDIR']
video_extensions=os.environ['NZBPO_VIDEOEXTENSIONS'].lower().split(',')
hb_cli=os.environ['NZBPO_CLIPATH']
preset=os.environ['NZBPO_PRESET']
outext=os.environ['NZBPO_OUTPUTEXTENSION']

# Make base directories for the queue and output if they don't exist
if not os.path.exists(queue_dir):
    print('[INFO] QueueDir "%s" doesn\'t exist. Creating.' % queue_dir)
    os.makedirs(queue_dir)
if not os.path.exists(out_dir):
    print('[INFO] OutDir "%s" doesn\'t exist. Creating.' % out_dir)
    os.makedirs(out_dir)

check_handbraked = os.system("ps aux | grep [h]andbraked")
if check_handbraked != 0:
    # Need to send output to /dev/null in so that handbraked will let this script exit
    FNULL = open(os.devnull, 'w')
    command = ["%s/handbraked" % current_script_dir, "--handbrake-cli", hb_cli, "--preset", preset, "--queue", queue_dir]
    subprocess.Popen(command, stdout=FNULL, stderr=subprocess.STDOUT)

final_dir = os.environ['NZBPP_FINALDIR']

vidfiles = []
for vidext in video_extensions:
    vidfiles.extend(glob.glob("%s/*%s" % (final_dir, vidext)))

in_dir = os.environ['NZBOP_DESTDIR']
in_dir_abs_path = os.path.abspath(in_dir)

for vidfile in vidfiles:
    vidfile_abs_path = os.path.abspath(vidfile)
    vidfile_relative_path = os.path.relpath(vidfile_abs_path, in_dir_abs_path)
    vidfile_relative_noext = os.path.splitext(vidfile_relative_path)[0]
    vidfile_out_path = "%s/%s.%s" % (out_dir, vidfile_relative_noext, outext)
    vidfile_queue_path = "%s/%s.json" % (queue_dir, vidfile_relative_noext.replace("/", "-"))

    if not os.path.exists(vidfile_out_path):
        f = open(vidfile_queue_path,'w')
        f.write('{\n  "in": "%s",\n  "out": "%s"\n}' % (vidfile_abs_path, vidfile_out_path))
        f.close()

    print('[INFO] Queued "%s" for HandBrake processing' % vidfile_relative_path)

sys.exit(POSTPROCESS_SUCCESS)