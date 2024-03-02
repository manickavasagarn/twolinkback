"""
 Copyright (c) 2018-2021 Intel Corporation

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""
import cv2


import numpy as np

#from model_api.utils import resize_image



def resize_image(image, size, keep_aspect_ratio=False, interpolation=cv2.INTER_LINEAR):
    if not keep_aspect_ratio:
        resized_frame = cv2.resize(image, size, interpolation=interpolation)
    else:
        h, w = image.shape[:2]
        scale = min(size[1] / h, size[0] / w)
        resized_frame = cv2.resize(image, None, fx=scale, fy=scale, interpolation=interpolation)
    return resized_frame
def crop(frame, roi):
    p1 = roi.position.astype(int)
    p1 = np.clip(p1, [0, 0], [frame.shape[1], frame.shape[0]])
    p2 = (roi.position + roi.size).astype(int)
    p2 = np.clip(p2, [0, 0], [frame.shape[1], frame.shape[0]])
    return frame[p1[1]:p2[1], p1[0]:p2[0]]


def cut_rois(frame, rois):
    return [crop(frame, roi) for roi in rois]


def resize_input(image, target_shape, nchw_layout):
    if nchw_layout:
        _, _, h, w = target_shape
    else:
        _, h, w, _ = target_shape
    resized_image = resize_image(image, (w, h))
    if nchw_layout:
        resized_image = resized_image.transpose((2, 0, 1)) # HWC->CHW
    resized_image = resized_image.reshape(target_shape)
    return resized_image


import numpy as np
import typing
import time
import cv2

class FPSmetric:
    """ Measure FPS between calls of this object
    """
    def __init__(
        self, 
        range_average: int = 30,
        position: typing.Tuple[int, int] = (7, 70),
        fontFace: int = cv2.FONT_HERSHEY_SIMPLEX,
        fontScale: int = 3,
        color: typing.Tuple[int, int, int] = (100, 255, 0),
        thickness: int = 3,
        lineType: int = cv2.LINE_AA,
        ):
        """
        Args:
            range_average: (int) = 30 - number of how many call should be averaged for a result
            position: (typing.Tuple[int, int]) = (7, 70) - position in a frame where to put text
            fontFace: (int) = cv2.FONT_HERSHEY_SIMPLEX - cv2 font for text
            fontScale: (int) = 3 - size of font
            color: (typing.Tuple[int, int, int]) = (100, 255, 0) - RGB color for text
            thickness: (int) = 3 - chickness for text
            lineType: (int) = cv2.LINE_AA - text line type
        """
        self._range_average = range_average
        self._frame_time = 0
        self._prev_frame_time = 0
        self._fps_list = []

        self.position = position
        self.fontFace = fontFace
        self.fontScale = fontScale
        self.color = color
        self.thickness = thickness
        self.lineType = lineType

    def __call__(self, frame: np.ndarray = None) -> typing.Union[bool, np.ndarray]:
        """Measure duration between each call and return calculated FPS or frame with added FPS on it

        Args:
            frame: (np.ndarray) - frame to add FPS text if wanted

        Returns:
            fps: (float) - fps number if frame not given otherwise return frame (np.ndarray)
        """
        self._prev_frame_time = self._frame_time
        self._frame_time = time.time()
        if not self._prev_frame_time:
            return frame
        self._fps_list.append(1/(self._frame_time - self._prev_frame_time))
        self._fps_list = self._fps_list[-self._range_average:]
        
        fps = float(np.average(self._fps_list))

        if frame is None:
            return fps

        cv2.putText(frame, str(int(fps)), self.position, self.fontFace, self.fontScale, self.color, self.thickness, self.lineType)
        return frame