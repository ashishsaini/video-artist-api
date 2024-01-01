from math import ceil
from playwright.sync_api import sync_playwright
import os
from uuid import uuid4
import time
import pathlib
import subprocess

class Recorder:

    def __init__(self, resolution):
        self.video_url = ""
        self.duration = 0 
        self.video_dir = "data/videos"
        self.height = resolution['height']
        self.width = resolution['width']

    def is_element_loaded(page, selector):
        return page.evaluate('''() => {
            const element = document.querySelector('img');
            // Check some property of the element to determine if it's loaded
            return element && element.offsetHeight > 0; // Example condition
        }''')

    
    def run(self, playwright):

        if not os.path.exists(self.video_dir):
            os.mkdir(self.video_dir)

        cache_dir = "/tmp/playwright_cache"  # Directory for caching
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)

        
        

        ## fake visit to enable cache
        print(">> starting cold start visit..")
        browser_context_options_fake = {
            'viewport': {'width': self.width, 'height': self.height}
        }

         # Use launch_persistent_context to enable caching
        context = playwright.chromium.launch_persistent_context(
            cache_dir,
            headless=True,
            # ignore_default_args=['--mute-audio'],
            args=['--autoplay-policy=no-user-gesture-required'],
            channel='chrome',
            # executable_path='/usr/bin/google-chrome',
            **browser_context_options_fake
        )

        page = context.new_page()
        page.set_viewport_size({'width': self.width, 'height': self.height})
        # page.wait_for_url("https://cdn.mage.space/generate/b20015da187147b4b219532475fdc3bc.jpg")

        page.goto(self.video_url, wait_until='networkidle')

        context.close()
        print(">> cold start visit done..")

        print(">> starting real visit...")
        browser_context_options = {
            'viewport': {'width': self.width, 'height': self.height},
            'record_video_dir': self.video_dir,
            'record_video_size': {'width': self.width, 'height': self.height}
        }

        # Use launch_persistent_context to enable caching
        context = playwright.chromium.launch_persistent_context(
            cache_dir,
            headless=True,
            # ignore_default_args=['--mute-audio'],
            args=['--autoplay-policy=no-user-gesture-required'],
            channel='chrome',
            # executable_path='/usr/bin/google-chrome',
            **browser_context_options
        )
        st = time.time()

        page = context.new_page()
        # page.set_viewport_size({'width': self.width, 'height': self.height})
        # page.wait_for_url("https://cdn.mage.space/generate/b20015da187147b4b219532475fdc3bc.jpg")

        page.goto(self.video_url, wait_until='load', timeout=1000000)
        browser_load_time = time.time() - st
        print("browser load time: ", browser_load_time)
        print("page loaded, sleeping for ", int(self.duration) / 1000)
        page.wait_for_timeout(int(self.duration))
        
        path = page.video.path()
        context.close()
        page.close()
        

        print("path: ", path)
        return path, browser_load_time

    
    def get_duration(self, filename):
        duration = 0
        try:
            command = "ffprobe -i {} -show_entries format=duration -v quiet -of csv=\"p=0\"".format(filename)
            print(command)
            duration = subprocess.check_output(command, shell=True)
            duration = float(duration)
        except Exception as e:
            print("error: ", e)
            duration = 0
        return duration


    def combine_audio_video(self, audio_file, video_path):

        filename = str(uuid4())    
        # combine audio and video using ffmpeg
        command = f"ffmpeg -i {audio_file} -i {video_path} -c:v copy -c:a aac -strict experimental {self.video_dir}/tmp-{filename}.mp4"
        print("Combine command: ", command)
        os.system(command)
        return f"{self.video_dir}/tmp-{filename}.mp4"


    def record(self, url, duration, audio_file):
        self.video_url = url
        self.duration = duration

        print(f"recording video {self.video_url} for ", duration, " seconds")

        video_path = ""
        load_time = 0
        with sync_playwright() as playwright:
            video_path, load_time = self.run(playwright)

        time.sleep(1)
        duration_1 = self.get_duration(video_path)

        print("duration_1: ", duration_1)
        start_time = duration_1 - load_time
        load_time = ceil(load_time)

        # use ffmpeg to remove loading part from begining, total duration should be self.duration
        filename = video_path.split("/")[-1].split(".")[0]
        command = "ffmpeg -i {} -ss 00:00:{} -async 1 {}/{}-cut.mp4".format(video_path, int(load_time), self.video_dir, filename)
        print(command)
        os.system(command)
        video_duration = self.get_duration(f"{self.video_dir}/{filename}-cut.mp4")
        print("video_duration: ", video_duration)

        time.sleep(1)

        # combine video and audio
        video_path = self.combine_audio_video(audio_file, f"{self.video_dir}/{filename}-cut.mp4")
        print("Final video_path: ", video_path)
        return video_path
        
    def combine_audio_video2(self, audio_url, video_path):

        filename = str(uuid4())

        # download audio from web to audios directory
        command = "wget -O audios/{}.mp3 {}".format(filename, audio_url)
        print(command)
        os.system(command)

        # convert webm to mp4
        command = "ffmpeg -i {} -hide_banner -loglevel error -c:v libx264 -crf 1 -vf \"scale=780:1440\" videos/{}.mp4".format(video_path, filename)
        print(command)
        os.system(command)

        #clip first 2 seconds of video
        # command = "ffmpeg -i videos/{}.mp4 -ss 00:05 --c:v libx264 -c:a videos/cut-{}.mp4".format(filename, filename)
        command = "ffmpeg -i  videos/{}.mp4 -ss 2 -async 1 videos/cut-{}.mp4".format(filename, filename)
        print(command)
        os.system(command)

        # command = "ffmpeg -i videos/cut-{}.mp4 -hide_banner -loglevel panic -vf \"setpts=0.88*PTS\" videos/speed-{}.mp4".format(filename, filename)
        # print(command)
        # os.system(command)

        # combine audio and video using ffmpeg
        command = "ffmpeg -i {} -i {} -hide_banner -loglevel panic -c:v copy -c:a aac -strict experimental {}".format(
            "audios/"+filename+".mp3", "videos/cut-"+filename+".mp4", "done/tmp-"+filename+".mp4")
        print(command)
        os.system(command)

        # add background music
        command  = "ffmpeg -i done/tmp-{}.mp4 -i bg_music/cartoon1.wav -hide_banner -loglevel panic -filter_complex \"[0:a][1:a]amerge=inputs=2[a]\" -map 0:v -map \"[a]\" -c:v copy -ac 2  done/tmp2-{}.mp4".format(filename, filename)
        print(command)
        os.system(command)

        # remove tmp files
        command = "rm done/tmp-{}.mp4".format(filename)
        print(command)
        os.system(command)

        current_dir = pathlib.Path(__file__).parent.resolve()
        video_file = f"done/tmp2-{filename}.mp4"

        # filename = video_file.split("/")[-1].split(".")[0]

        wav_outpath = f"{current_dir}/tmp/{filename}.wav"
        srt_path = f"{current_dir}/tmp/{filename}"
        # get audio from video 
        os.system(f"ffmpeg -y -i {video_file} -ar 16000  {wav_outpath}")

        os.system(f"cd ../whisper/whisper.cpp-master/ && ./main -m models/ggml-medium.en.bin -f {wav_outpath} --split-on-word --max-len 8 --output-srt  --output-file {srt_path}")
                
        srt_path = srt_path+".srt"

        # print(f"ffmpeg -i {video_file} -f srt -i {srt_path} -map 0:0 -map 0:1 -map 1:0 -c:v copy -c:a copy -c:s mov_text tmp/out.mp4")
        command = f"ffmpeg -y -i {video_file} -vf \"subtitles={srt_path}:fontsdir=/home/ashy/code/story-shorts/oswald:force_style='Fontname=Oswald,PrimaryColour=&H80ffffff,Bold=1,Italic=0,Spacing=0.8,Alignment=2,OutlineColour=&H00000000,Outline=3,Background=&H00000000,FontSize=16,MarginV=70'\" -c:a copy done/final-{filename}.mp4"
        print("subtitles command: ", command)
        os.system(command)

        return "done/final-"+filename+".mp4"


if __name__ == "__main__":
    recorder = Recorder()
    path = recorder.record("http://google.com",  5000.0)
    print("path: ", path)


    # video_path = recorder.combine_audio_video("http://localhost:7070/data/audio/555f2e60-91a0-48ce-b80b-7e4ed4049d2d/7ac798e3-d191-4bea-9866-eb17ab5c477f.mp3", path)   
    # print("video_path: ", video_path)