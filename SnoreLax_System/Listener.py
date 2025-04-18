import subprocess
import wave
import numpy as np
import time
import os
import signal
from datetime import datetime
from Classifier import analyze_sleep_recordings

    # Global variables for volume threshold and silence period control
volumeThreshold = 0.002
silencePeriod = 10

class ThresholdAudioRecorder:
    def __init__(self, 
                 threshold=volumeThreshold,               # Volume threshold
                 silence_timeout=silencePeriod,           # Stop recording after this many seconds of silence
                 rate=16000,                              # Sampling rate - higher increases quality but also takes more disk space, 16khz is more than enough
                 channels=1,                              # Mono audio
                 chunk=1024,                              # Frames per buffer
                 output_dir="sleep_recordings"):          # Directory for saved recordings
        
        currentDate = datetime.now().strftime("%Y%m%d")
        output_dir = f"{output_dir}/{currentDate}"

        self.threshold = threshold
        self.silence_timeout = silence_timeout
        self.rate = rate
        self.channels = channels
        self.chunk = chunk
        self.output_dir = output_dir
        self.device = "plughw:NTUSB"  # Røde NT-USB microphone, posed some problems with default and undetected device

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Starts monitoring for sounds, if sounds are detected, then it will start recording
    def start_monitoring(self, duration=None):
        print(f"Starting audio monitoring. Threshold: {self.threshold}")
        print(f"Will record until {self.silence_timeout} seconds of silence")
        print(f"Press Ctrl+C to stop monitoring")
        

        temp_file = "temp_monitor.wav"
        start_time = time.time()
        last_recording_end = 0
        cooldown_period = 1
        
        try:
            while True:
                if duration and (time.time() - start_time) > duration:
                    print(f"Monitoring duration ({duration}s) elapsed")
                    break
                
                    # Records a sample to test volume level, and start recoring if threshold is exceeded
                self.record_sample(temp_file, 1) 
                volume = self.get_audio_level(temp_file)
                
                current_time = time.time()
                if volume > self.threshold and (current_time - last_recording_end) > cooldown_period:
                    timestamp = datetime.now().strftime("%Y%m%d__%H%M%S")
                    filename = os.path.join(self.output_dir, f"rec_{timestamp}.wav")
                    
                    print(f"\nSound detected! Volume: {volume:.4f}")
                    print(f"Recording until {self.silence_timeout}s of silence...")
                    
                    self.record_until_silence(filename)
                    last_recording_end = time.time()
                
                    # Visual for volume level
                if volume > self.threshold * 0.5:
                    bars = int(volume * 50)
                    print(f"\rVolume: {'|' * bars:<50} {volume:.4f}", end="")
                
                    # Delete temp file after sampling
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
        
        except KeyboardInterrupt:
            print("\nVolume monitoring stopped by the user")
        finally:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    

    def record_sample(self, filename, duration):
        cmd = ["arecord", "-D", self.device, "-f", "S16_LE", "-c", str(self.channels),
            "-r", str(self.rate), "-d", str(duration),"-q", filename]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            print("\rError recording audio sample", end="")
            return False
    

        # Analyzes the audio and calculate volume level
    def get_audio_level(self, filename):
        try:
            with wave.open(filename, 'rb') as wf:
                n_frames = wf.getnframes()
                data = wf.readframes(n_frames)
                audio_data = np.frombuffer(data, dtype=np.int16)
                

                if len(audio_data) > 0:
                    mean_square = np.mean(np.square(audio_data.astype(np.float32)))
                    if np.isnan(mean_square) or mean_square < 0:
                        return 0
                    return np.sqrt(mean_square) / 32767
                return 0
        except Exception as e:
            print(f"\rError analyzing audio: {e}", end="")
            return 0
    
        # Records audio until silence is detected
    def record_until_silence(self, filename):
        temp_filename = "temp_recording.wav"
        cmd = ["arecord", "-D", self.device, "-f", "S16_LE", "-c", str(self.channels),
            "-r", str(self.rate), "-d", str(duration),"-q", temp_filename]

        recording_process = subprocess.Popen(cmd)
        frames = []
        silent_chunks = 0
        
        silent_chunks_threshold = int(self.silence_timeout)
        
        print(f"Recording... (will stop after {silent_chunks_threshold} seconds of silence)")
        
        recording_start_time = time.time()
        check_file = "temp_check.wav"
        
        while silent_chunks < silent_chunks_threshold:
            time.sleep(1)
            self.record_sample(check_file, 1)
            volume = self.get_audio_level(check_file)
            
            if volume <= self.threshold:
                silent_chunks += 1
                seconds_left = silent_chunks_threshold - silent_chunks
                print(f"\rSilence detected: {seconds_left}s until recording stops", end="")
            else:
                silent_chunks = 0
                duration = time.time() - recording_start_time
                print(f"\rRecording... Duration: {duration:.1f}s", end="")
            

            if os.path.exists(check_file):
                try:
                    os.remove(check_file)
                except:
                    pass
        
        recording_process.send_signal(signal.SIGINT)
        recording_process.wait()
        
        endTimestamp = datetime.now().strftime("-%H%M%S")
        final_filename = filename.replace(".wav", endTimestamp + ".wav")
        print(f"\n\nRecording stopped. Saving to {final_filename}...")


        if os.path.exists(temp_filename):
            os.rename(temp_filename, final_filename)
            
            try:
                with wave.open(final_filename, 'rb') as wf:
                    duration = wf.getnframes() / wf.getframerate()
                print(f"Finished recording. Duration: {duration:.1f}s")
            except Exception as e:
                duration = time.time() - recording_start_time
                print(f"Finished recording. Estimated duration: {duration:.1f}s")
            analyze_sleep_recordings(final_filename)
        else:
            print("Error: Recording file not found")


if __name__ == "__main__":
    recorder = ThresholdAudioRecorder(
        threshold=volumeThreshold,
        silence_timeout=silencePeriod,
        output_dir="sleep_recordings"
    )
    
    try:
        recorder.start_monitoring()
    finally:
        pass