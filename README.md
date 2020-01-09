# GIF Generator
a simple gif generator, which can edit video and do some image enhancement and segmentation

## Introduction
After open a file, you can use `pin` button to record target video, after recording, click `complete` to enter edit mode, then you can do some image enhancement and effect. After editing, click `save` to save GIF. You can click `stop` & `play` to stop/play video at any time.  

## Feature
 * Nagative film
 
 * Gamma Correction
     > paramater: Gamma (default:20)
 * Light Flash: a flashlight like light implement on image
      > paramater: Flash duration ( Every few frames) (default:5)
 * Shake: (animation) image shake
     > paramater: Shake level(a few pixels)(default:5)
 * Slide: (animation) image slide to specify direction
     > paramater: Slide Direction(default:right)
 * Segmenatation : to do person segmenatation
     > paramater: Background color(default:#000000)
 * foreground: change foreground image and add some simple animation
    > chose animation then chose the image wanted and click the button
 *  background: change background image and add some simple animation
    > chose animation then chose the image wanted and click the button
 *  Gaussian Blur
    > paramater: Kernel Size(default:7)
 *  Canny Edge Detect
    > paramater: Lower And Upper Bound(default:30,160)
 *  Gaussian Noise
    > paramater: Noise Level(Range:0-255)(default:40)
 *  White Point Noise :special effect
    > paramater:  Update Duration(default:3)
 *  Add text:  add text on image
    > paramater: string(default:1 6 3 b r a c e s), font-size(default: 48), text-color(default: #cd8068), text-position(default: (250,200)),font (choose on listbox)


## Usage 
download and install dependency package, and use python compiler to run `Main.py` 

## License 
NCU　CSIE 陳昱瑋

## Contact
210509fssh@gmail.com
