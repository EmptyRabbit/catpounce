from typing import Tuple, List


class CoordinateUtil():
    @staticmethod
    def normalization_1000(bbox: List[int], screen_width: int, screen_height: int) -> Tuple[List[int], float, float]:
        actual_bbox = [
            int(bbox[0] * screen_width / 1000),
            int(bbox[1] * screen_height / 1000),
            int(bbox[2] * screen_width / 1000),
            int(bbox[3] * screen_height / 1000),
        ]
        actual_x_min, actual_y_min, actual_x_max, actual_y_max = actual_bbox
        wd, ht = actual_x_max - actual_x_min, actual_y_max - actual_y_min

        actual_x = actual_x_min + wd / 2
        actual_y = actual_y_min + ht / 2
        return actual_bbox, actual_x, actual_y
