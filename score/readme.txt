=================== general =====================
Running on Ubuntu 11.04.  10.x seems to be missing various sound FX plugins for Rosegarden so...


=================== jack =====================
use qjackctl
for headphones/alt output: setup/interface (arrow to right pulls down menu)

=================== fluidsynth =====================
install fluidsynth-DSSI ++
this bugger, while great, uses absolute paths for samples, so I've created a symlink /fluidsynth, which should point
to score/fluidsynth

=================== rosegarden =====================
note rosegarden runs jack with last settings if you don't run jack manually
double-click .rg file (rosegarden)
often main screen appears in wrong workspace (find it) -- you just see transport
if new machine: fiddle with jack setup for buffer stuff


=================== timemachine =====================
to record:

after running jack + rosegarden, run timemachine -f wav
go to jack connect menu
highlight rosegarden on left, timemachine on right
right click and select "connect"
hit the big red button to record
note it seems to leave lots of dead time at top (recording always?)
use audacity to trim & export to mp3
