

Try to detect ‘significant motion’ using frame differencing technique. The proposed solution is based upon the instantiating an object, called BlankSeqRemoval with next parameters:  

**out_vid_name**: string - name of the video file where unremoved sequences (frames) will be stored. This file will be saved in the current directory as .avi file. Default is to an empty string.  

**kernel_size**: int – an odd positive integer that is the magnitude of noise removal that will be applied for each frame for better further processing. The higher the value, the blurrier the frame will become, therefore less noise will be present in the frame and less unnecessary noise pixels will be present. This is useful for setting how much the pixel noise should be removed. Default is set to 7.  

**min_area**: int - is the minimum pixel area threshold that needs to be surpassed by a detected moving objects in order for the algorithm to make the distinction between motion or noise, e.g. falling leaf with small motion detected area is perceived as noise whereas a car which has a much higher motion detected area is perceived as significant motion. Default is 700.  

**lot_of_noise_det**: Boolean – is a flag that specifies if lots of small motion detected areas (noise) should be detected as significant motion. This is useful for sudden illumination changes. Default is False.  

**Mov_detected_pixels_threshold**: int – needs to be specified in case if lot_of_noise_det is set to True and therefore lot of noise detection is activated. Default is 20000  

The BlankSeqRemoval object contains a method called frame_diff() that is responsible with detecting motion using frame differencing technique applied in real-time between the current frame and the previous frame.  

The method frame_diff() captures frame-by-frame a live video stream that is coming from a camera device that has the device index set to 0 (usually it’s the pc webcam). The frame differencing is made in real-time and the processing is heavily based upon the given BlankSeqRemoval parameters. At each step (frame), the current frame is absolutely differentiated with the previous frame in order to extract any kind of motion that occurs between these two frames. Now, the terminology of ‘motion’ in this context is split into four categories:  

1. **No significant motion** – which translates into the case when between the current frame and the previous frame there is no motion detected. The current frame in this case will be marked as blank with a red cross that is drawn across the entire frame.
2. **Noise motion** – is the case when between the current frame and the previous there’s one or more small motion detected areas that do not surpass the min_area threshold. In this case the frame will be also marked as blank.
3. **‘Significant motion’** - is the case when between the current frame and the previous there’s one or more motion detected areas that do surpass the min_area. In this case the current frame will be saved in the output video stream in the file named out_vid_name.avi
4. **Lots of noise motion** – there are some cases when a lot of noise (small motion detected areas) within the frame. An example of such cases would be sudden illumination changes where a lot of noise suddenly pops out and therefore small detected areas are present. In some cases, this kind of aggregated noise can be perceived as significant motion, therefore if all this small areas detected motions are covering enough pixels that summed up are exceeding the mov_detected_pixels_threshold, then these aggregated noises may be perceived as a significant motion and therefore the current frame will be saved, otherwise it will still mark it as insignificant motion.