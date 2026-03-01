import base64
import os


class ImageUtil():
    @staticmethod
    def save_png(base64_str: str, dir_path: str, file_name: str):
        image_data = base64.b64decode(base64_str)
        os.makedirs(dir_path, exist_ok=True)
        path = os.path.join(dir_path, file_name)

        with open(path, 'wb') as f:
            f.write(image_data)

        return path
