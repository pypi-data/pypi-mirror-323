from yta_multimedia.video.parser import VideoParser
from yta_image.parser import ImageParser
from yta_general_utils.programming.parameter_validator import NumberValidator
from moviepy import ImageClip
from moviepy.Clip import Clip
from typing import Union, Any
import numpy as np


def generate_video_from_image(
    image: Union[str, Any, ImageClip],
    duration: float = 1,
    fps: float = 30,
    output_filename: Union[str, None] = None
):
    """
    Receives an image and creates an ImageClip of 'duration' seconds.
    It will be also stored as a file if 'output_filename' is provided.
    """
    if not NumberValidator.is_positive_number(duration):
        raise Exception(f'The provided "duration" parameter {str(duration)} is not a positive number.')

    if not isinstance(image, ImageClip):
        video = ImageClip(ImageParser.to_numpy(image), duration = duration).with_fps(fps)

    if output_filename:
        video.write_videofile(output_filename)

    return video

def is_video_transparent(video: Clip):
    """
    Checks if the first frame of the mask of the
    given 'video' has, at least, one transparent
    pixel.
    """
    # We need to detect the transparency from the mask
    video = VideoParser.to_moviepy(video, do_include_mask = True)

    # We need to find, by now, at least one transparent pixel
    # TODO: I would need to check all frames to be sure of this above
    # TODO: The mask can have partial transparency, which 
    # is a value greater than 0, so what do we consider
    # 'transparent' here (?)
    return np.any(video.mask.get_frame(t = 0) == 1)