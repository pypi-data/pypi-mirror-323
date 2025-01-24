import cv2
import threading
import time
from datetime import datetime


class VideoStream:
    """
    This class is used to read the video stream from the given RTSP URL
    """
    def __init__(self, rtsp_url):
        """
        Initializes the VideoStream class and starts the thread to read the video stream
        :param rtsp_url: str -> RTSP URL of the camera
        """
        self.rtsp_url = rtsp_url
        self.frame = None
        self.running = True
        self.thread = threading.Thread(target=self.update, args=())
        self.cap = None
        self.set_cap()
        self.thread.daemon = True  # Close the thread with main thread
        self.thread.start()

    def set_cap(self):
        """
        This function is used to set the capture object which connects to the RTSP URL
        :return: None
        """
        self.cap = cv2.VideoCapture(self.rtsp_url)
        if not self.cap.isOpened():
            while not self.cap.isOpened() and self.running:
                self.cap = cv2.VideoCapture(self.rtsp_url)
                time.sleep(1)

    def update(self):
        """
        This function is used to read the frames from the video stream and when the frame is read, it updates the frame
        and if the frame is not read, it sets the frame to None and releases the capture object and sets it again.
        :return: None
        """
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame
            else:
                self.frame = None
                print("Feed Dropped at root at: ", str(int(datetime.now().timestamp() * 1000)))
                self.cap.release()
                self.set_cap()

    def read(self):
        """
        This function is used to get the frame from the video stream
        :return: np.array -> Frame from the video stream
        """
        return self.frame

    def get_fps(self):
        """
        This function is used to get the FPS of the video stream
        :return: int -> FPS of the video stream
        """
        return self.cap.get(cv2.CAP_PROP_FPS)

    def get_frame_width(self):
        """
        This function is used to get the frame width of the video stream
        :return: int -> Frame width of the video stream
        """
        return self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    def get_frame_height(self):
        """
        This function is used to get the frame height of the video stream
        :return: int -> Frame height of the video stream
        """
        return self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def stop(self):
        """
        This function is used to stop the video stream and release the capture object
        :return: None
        """
        self.running = False
        self.frame = None
        self.thread.join()
        self.cap.release()
