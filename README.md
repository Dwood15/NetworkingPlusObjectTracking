# NetworkingPlusObjectTracking
A demonstration of Object Tracking and networking between a Pi and a PC

Intention: 
  Designed for the BYUI Research and Creative Works Conference, this project requires some information to set up properly.
  
Notes:  
  Unreal Engine v. 4.12.5 is used in the .CPP and .H files. The Networking is simplistic.
  
    In any new project for Unreal, there is an included "*.build.cs" file which helps building the game. 
    When you create a new project, and want to use the Networking and Sockets project, you need to add them to the "PublicDependency ModuleNames" in that file.
    See the example "QuickStart.Build.cs" file for more information. 
    
  Python 3+ is recommended for the Pi. It could be converted to a USB camera and moved directly to the PC easily.
  
    To utiltize OpenCV 3.1 on the Pi, you will need to build your own version or find a prebuilt one for  the Pi and add the appropriate bindings for the path. 
    There are tutorials to do it, so I'm not concerned about providing my own.
    
Future Ideas: 
  Performance issues. the Pi currently puts out about 24 FPS from the object tracking. It should be able to pump out 60 fps much more effectively. Researching into the depths of the Pi's libraries and such to gain more control over it. This entails a move to Python and potentially chaning some settings. the Pi is slow, yes, but at 360x240 it should be able to do 30 fps minimum. Also, there is some autofocusing going on from the camera when I choose 60fps and I don't like it.
  
  The networking is slow on the PC and the Pi has some trouble sending data over TCP - consider moving to UDP and threading the networking updates.
  
  Adding depth-tracking for distance-to-camera magic. I have some functions in the Py script alluding to it, but nothing was done because the tuning for the object tracking is all over the place.
  
  If you have questions, feel free to comment/message me. I check my messages every few days. 
