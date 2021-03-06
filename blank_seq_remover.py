from imutils.video import VideoStream
from cv2 import cv2
import numpy as np
import argparse
import datetime
import imutils
import time

WHITE_PIXEL_VALUE = 255

class BlankSeqRemoval:
    def __init__(self,out_vid_name='',mov_detected_pixels_threshold=30, kernel_size=7, lot_of_noise_det=False, history = 10,min_area=700):
        self.video_capture = cv2.VideoCapture(0)
        self.mog2 = cv2.createBackgroundSubtractorMOG2(
            history=history,
            varThreshold=50,
            detectShadows=True
        )
        self.knn = cv2.createBackgroundSubtractorKNN(history=10)
        self.current_frame = None 
        self.previous_frame = None # initially there is no previous frame
        self.kernel_size = kernel_size
        self.min_area = min_area
        self.lot_of_noise_det = lot_of_noise_det
        self.cap_frame_width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.cap_frame_height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        codec = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(out_vid_name+'.avi', codec, 20.0, (self.cap_frame_width, self.cap_frame_height))
        self.mov_detected_pixels_threshold = mov_detected_pixels_threshold*WHITE_PIXEL_VALUE
        

    def mark_as_removed(self,frame):
        # Draws the red diagonal lines
        cv2.line(frame, pt1=(0, 0), pt2=(frame.shape[1], frame.shape[0]), color=(0, 0, 255), thickness=8)
        cv2.line(frame, pt1=(0, frame.shape[0]), pt2=(frame.shape[1], 0), color=(0, 0, 255), thickness=8)

    def frame_diff(self):        
        _ , self.previous_frame = self.video_capture.read()
        while (True): 

            _ , self.current_frame = self.video_capture.read()        

            # compute the absolute difference between the current frame and previous frame
	        # convert it to grayscale, and blur it
            diff = cv2.absdiff(self.previous_frame, self.current_frame)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (self.kernel_size,self.kernel_size), 0)
            _ , thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            # dilate the thresholded image to fill in holes, then find contours on thresholded image
            dilated = cv2.dilate(thresh, None, iterations=3)          
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            movement_flag = False
            for contour in contours:
                if cv2.contourArea(contour) < self.min_area:
                    continue
                movement_flag = True

            show_frame = np.copy(self.current_frame)
            if self.lot_of_noise_det:
                white_pixels_count = np.sum(dilated)
                if not movement_flag and white_pixels_count < self.mov_detected_pixels_threshold:
                    self.mark_as_removed(show_frame)
                else:
                    self.video_writer.write(self.current_frame)
            else:
                if not movement_flag:
                    self.mark_as_removed(show_frame)
                else:
                    self.video_writer.write(self.current_frame)

            # cv2.imshow("Live Contours", self.previous_frame)
            cv2.drawContours(show_frame, contours, -1, (0, 255, 0), 2)
            cv2.imshow("Live Feed", show_frame)
            cv2.imshow("Dilated", dilated)
            cv2.imshow("Frame Delta", gray)

            self.previous_frame = self.current_frame

            if cv2.waitKey(60) & 0xFF == ord('q'): 
                break

    def mog(self):
        while(True):
            self.previous_frame = self.current_frame
            # Capture the video frame by frame
            _ , self.current_frame = self.video_capture.read()
            # Do not initiate the processing if there's no previous frame so skip the first loop
            if (self.previous_frame is None):
                continue             
        
            # Apply gray conversion and noise reduction (smoothening) for better and faster processing
            current_frame_gray = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
            current_frame_gray = cv2.GaussianBlur(current_frame_gray, (self.kernel_size, self.kernel_size), 0)
            cv2.imshow('gray',current_frame_gray)
            
            foreground_mask = self.mog2.apply(current_frame_gray, fgmask=None, learningRate=-1) 
            # fmask is the output foreground mask as an 8-bit binary image.
            # Next video frame. Floating point frame will be used without scaling and should be in range [0,255].
            # learningRate	The value between 0 and 1 that indicates how fast the background model is learnt.
            # Negative parameter value makes the algorithm to use some automatically chosen learning rate. 
            # 0 means that the background model is not updated at all, 1 means that the background model is completely reinitialized from the last frame.
            cv2.imshow('Foreground Mask', foreground_mask)

            white_pixels_count = np.sum(foreground_mask)
            if white_pixels_count < self.mov_detected_pixels_threshold:
                self.mark_as_removed(self.current_frame)
            else:
                self.video_writer.write(self.current_frame)

            cv2.imshow("Live Feed", self.current_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break                

    def stop_capture(self):
        self.video_capture.release()
        cv2.destroyAllWindows() 

bsr = BlankSeqRemoval(out_vid_name='out',kernel_size=5,history=1000,mov_detected_pixels_threshold=20000,lot_of_noise_det=False, min_area= 2500)
bsr.frame_diff()
# bsr.mog()
bsr.stop_capture()

