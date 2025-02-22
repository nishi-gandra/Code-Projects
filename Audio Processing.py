"""
6.101 Lab 0:
Audio Processing
"""

import wave
import struct
# No Additional Imports Allowed!


def backwards(sound):
    backward = sound.copy()
    new_samples = list(backward['samples'])
    new_samples.reverse()
    backward.update({'samples':new_samples})
    return backward
    raise NotImplementedError


def mix(sound1, sound2, p):
    sound_1 = sound1.copy()
    sound_11 = list(sound_1['samples'])
    sound_2 = sound2.copy()
    sound_22 = list(sound_2['samples'])
    if sound_1['rate'] != sound_2['rate']:
        return None
    else:
        for i in range(len(sound_11)):
            sound_11[i] = sound_11[i] * p
        for j in range(len(sound_22)):
            sound_22[j] = sound_22[j] * (1 - p)
        mix_sample = []
        if len(sound_11) > len(sound_22):
            extra = len(sound_11) - len(sound_22)
            for i in range(extra):
                sound_22.append(0)
            for k in range(len(sound_22)):
                mix_sample.append(sound_11[k] + sound_22[k])
        else:
            extra = len(sound_22) - len(sound_11)
            for i in range(extra):
                sound_11.append(0)
            for k in range(len(sound_22)):
                mix_sample.append(sound_11[k] + sound_22[k])
    sound_1.update({'samples':mix_sample})
    return sound_1
    raise NotImplementedError


def convolve(sound, kernel):
    sound_1 = sound.copy()
    sound_11 = sound_1['samples']
    length = len(sound_11) + len(kernel) - 1
    convolve = [0] * length

    for i in range(len(kernel)):
        for j in range(len(sound_11)):
            convolve[i+j] = convolve[i+j] + sound_11[j] * kernel[i]

    sound_1.update({'samples':convolve})

    return sound_1
    raise NotImplementedError


def echo(sound, num_echoes, delay, scale):
    sound_1 = sound.copy()
    sound_11 = sound_1['samples'].copy()
    sound_12 = sound_1['samples'].copy()
    sample_delay = round(delay * sound['rate'])
    new_list = []
    length = int(num_echoes * sample_delay) + len(sound_11)
    for i in range(length):
        new_list.append(0)
    sound_11.extend([0] * (length - len(sound_11)))

    for i in range(1, num_echoes + 1):
        new_scale = scale ** i
        delay = sample_delay * i
        for j in range(delay,delay + len(sound['samples'])):
            new_list[j] = new_scale * sound_12[j - delay]
        sound_11 = [x + y for x,y in zip(sound_11,new_list)]
        new_list = []
        for i in range(length):
            new_list.append(0)

    sound_1.update({'samples':sound_11})
    return sound_1

    raise NotImplementedError


def pan(sound):
    sound_copy = sound.copy()
    sound_left = sound_copy['left'].copy()
    sound_right = sound_copy['right'].copy()
    sample = len(sound_right)
    for i in range(sample):
        sound_right[i] = sound_right[i] * (i/(sample-1))
        sound_left[i] = sound_left[i] * (1-(i/(sample-1)))
    sound_copy.update({'left':sound_left, 'right':sound_right})
    return sound_copy
    raise NotImplementedError


def remove_vocals(sound):
    sound_copy = sound.copy()
    sound_left = sound_copy['left'].copy()
    sound_right = sound_copy['right'].copy()
    sound_new = [x - y for x,y in zip(sound_left,sound_right)]
    sound = {'rate': sound_copy['rate'],
             'samples': sound_new,}
    return sound
    raise NotImplementedError


def bass_boost_kernel(n_val, scale=0):
    """
    Construct a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ n_val

    Then we scale that piece up and add a copy of the original signal back in.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    kernel = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    for i in range(n_val):
        kernel = convolve(kernel, base["samples"])
    kernel = kernel["samples"]

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel) // 2] += 1

    return kernel


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds


def load_wav(filename, stereo=False):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    file = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = file.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    if stereo:
        left = []
        right = []
        for i in range(count):
            frame = file.readframes(1)
            if chan == 2:
                left.append(struct.unpack("<h", frame[:2])[0])
                right.append(struct.unpack("<h", frame[2:])[0])
            else:
                datum = struct.unpack("<h", frame)[0]
                left.append(datum)
                right.append(datum)

        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = []
        for i in range(count):
            frame = file.readframes(1)
            if chan == 2:
                left = struct.unpack("<h", frame[:2])[0]
                right = struct.unpack("<h", frame[2:])[0]
                samples.append((left + right) / 2)
            else:
                datum = struct.unpack("<h", frame)[0]
                samples.append(datum)

        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for left, right in zip(sound["left"], sound["right"]):
            left = int(max(-1, min(1, left)) * (2**15 - 1))
            right = int(max(-1, min(1, right)) * (2**15 - 1))
            out.append(left)
            out.append(right)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


# if __name__ == "__main__":
#     # code in this block will only be run when you explicitly run your script,
#     # and not when the tests are being run.  this is a good place to put your
#     # code for generating and saving sounds, or any other code you write for
#     # testing, etc.

#     # here is an example of loading a file (note that this is specified as
#     # sounds/hello.wav, rather than just as hello.wav, to account for the
#     # sound files being in a different directory than this file)


#     # write_wav(backwards(hello), 'hello_reversed.wav')

# mystery = load_wav("sounds/mystery.wav")
# write_wav(backwards(mystery), 'mystery_reversed.wav')

# synth = load_wav("sounds/synth.wav")
# water = load_wav("sounds/water.wav")
# write_wav(mix(synth,water,0.2), 'mixed.wav')

# ice_and_chilli = load_wav("sounds/ice_and_chilli.wav")
# kernel = bass_boost_kernel(1000, scale=1.5)
# write_wav(convolve(ice_and_chilli,kernel), 'convolved.wav')

# chord = load_wav("sounds/chord.wav")
# write_wav(echo(chord, 5, 0.3, 0.6), 'chord.wav')

# car = load_wav("sounds/car.wav", stereo=True)
# write_wav(pan(car), 'car.wav')

# lookout_mountain = load_wav("sounds/lookout_mountain.wav", stereo=True)
# write_wav(remove_vocals(lookout_mountain), "lookout_mountain.wav")
