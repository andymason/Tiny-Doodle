Tiny Doodle
===========

Tiny Doodle is an exercise in learning about <canvas>.
Event handlers are attached the to <canvas> elemet for both
mouse and touch input devices. The user can doodle away on the
<canvas>, clear and save the resulting doodle.

Saving the doodle extracts the canvas data in base64 format,
POST's the string to a Python service which stores it in a 
database.