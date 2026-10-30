# Version 70 Meshy prompts (nano-banana-pro, image-to-image, 9 credits each)

Run with `MESHY_WORK=<dir> python3 tools/v64/meshy_free.py v70 <name> "<prompt>" <refs>`; results copied to tools/v70/img/<name>.webp and cut by tools/v70/cut.py.

- train, bus: a layout of the existing wall pieces with rough ceiling and floor bands; "keep the wall in the middle band exactly where it is" and describe the ceiling and floor. Refs: the layout, a Meshy stage tile, `street`.
- fg: four foreground objects on flat magenta (#FF00FF), side by side, "drawn very close to the camera, strong dark silhouettes".
- pit: the old 240x136 cut-in picture upscaled as the layout.
- darts: the old darts screen with a black circle the size of the board painted on it ("the big black circle stays exactly where it is and exactly as big"); the first two tries drew the board space too small.
- banner: one wide caption plate on magenta, with web/bg/hud/panel.png as the style.
- over, win: free pictures, "the middle left fairly plain so big text can go over it".
- icon: 1:1, with the title logo as a style reference.
- items: tools/v64/repaint.py items --make, LIGHT="bright, even, clean lighting".
