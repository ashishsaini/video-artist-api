'''
Do not download the video too many times
File keeps the record of 

'''
import os
import json


class MediaCache:

    def __init__(self, cache_dir) -> None:
        self.cache_dir = cache_dir
        self._check_and_create_dir(cache_dir)

    def _check_and_create_dir(self, dir):
        if not os.path.exists(dir):
            try:
                os.mkdir(dir)
            except Exception as e:
                print(f"Unable to create required downloads directory: {dir}")
                print(f"{e}")
                exit()
        return True

    def save(self, media_path, media_id):
        # save the media file path
        try:
            with open(os.path.join(self.cache_dir, self._get_cache_name(media_id)), "w") as f:
                data = {"media_path": media_path}
                f.write(json.dumps(data))
                print(f"media saved {media_path}")
        except Exception as e:
            print("Warning: unable to write data in media cache")
            return False
        return True

    def get(self, media_id):
        # return the media path if media exists
        filename = os.path.join(self.cache_dir, self._get_cache_name(media_id))
        data = {}
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f:
                    data = json.loads(f.read())
            except Exception as e:
                print("error in getting cache file")
                print(str(e))
                return False

        if not data:
            return False

        return data['media_path']

    def _get_cache_name(self, media_id):
        return "media_"+str(media_id)+".txt"
