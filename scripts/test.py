import subprocess


def generate_silence(duration, filepath):
    try:
        result = (subprocess.check_output(
            ['sox', '../files/1sec_silence.wav', 'new_file.wav', 'repeat', str(duration-1)]).decode().strip())
    except Exception as e:
        print(e)

    return result


print(generate_silence(12, "/tmp/"))
