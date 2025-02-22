#!/usr/bin/env python3

"""
6.101 Lab 1:
Image Processing
"""

import math

from PIL import Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, row, col):
    # returns the value of the pixel given its position in terms of row and column
    width = image["width"]
    position = row * width + col
    return image["pixels"][position]


def get_pixel_outside(image, row, col, boundary_behavior):
    # given a boundary behvior, this function fills in pixels that
    # are out of bounds for the kernels to successfully run
    image_row, image_col = image["height"], image["width"]
    if row < 0 or row >= image_row or col < 0 or col >= image_col:
        if boundary_behavior == "zero":
            return 0
        elif boundary_behavior == "extend":
            if row < 0:
                row = 0
            elif row >= image_row:
                row = image_row - 1
            # minus one because the range indexes to one higher than it needs to be (indexing starts at zero)
            if col < 0:
                col = 0
            elif col >= image_col:
                col = image_col - 1
        elif boundary_behavior == "wrap":
            if row < 0 or row >= image_row:
                row = row % image_row
            # getting the remainder grabs the right index number
            if col < 0 or col >= image_col:
                col = col % image_col
    return get_pixel(image, row, col)


def set_pixel(image, row, col, new_color):
    # inserts a new pixel for the old one given its position
    width = image["width"]
    position = row * width + col
    image["pixels"][position] = new_color


def apply_per_pixel(image, func):
    # applies a specific function to every value of the pixels
    image = {
        "height": image["height"],
        "width": image["width"],
        "pixels": image["pixels"].copy(),
    }
    for row in range(image["height"]):
        for col in range(image["width"]):
            color = get_pixel(image, row, col)
            new_color = func(color)
            set_pixel(image, row, col, new_color)
    return image


def inverted(image):
    # function to invert the color
    return apply_per_pixel(image, lambda color: 255 - color)


# HELPER FUNCTIONS


def correlate(image, kernel, boundary_behavior, edges=False):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will be one of the strings "zero", "extend", or "wrap",
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of "zero", "extend", or "wrap", return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with "height", "width", and "pixels" keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    Each kernel is a list of sublists in row order. Within each sublist,
    the kernel is in column order.
    """

    image_row, image_col = image["height"], image["width"]
    kernel_row, kernel_col = len(kernel), len(kernel[0])
    midpoint = len(kernel) // 2
    new_pixel_list = []

    if boundary_behavior not in ["zero", "extend", "wrap"]:
        return None
    # iterated through each row and column of the image as well as each row and column
    # of the kernel to multiply the value at the position given boundary behvaior with the kernel value.
    # These values are all added up until it's time to index into the position (row and col) of the original image.

    else:
        for i in range(image_row):
            for j in range(image_col):
                new_pixel = 0
                for m in range(kernel_row):
                    for p in range(kernel_col):
                        new_pixel += (kernel[m][p]) * get_pixel_outside(
                            image, i + m - midpoint, j + p - midpoint, boundary_behavior
                        )
                new_pixel_list.append(new_pixel)

        new_image = {
            "height": image_row,
            "width": image_col,
            "pixels": new_pixel_list,
        }
        # so that round and clip is not run when edges calls to the correlate function
        if edges == False:
            return new_image

        return round_and_clip_image(new_image)


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the "pixels" list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    for i in range(len(image["pixels"])):
        if image["pixels"][i] < 0:
            image["pixels"][i] = 0
        elif image["pixels"][i] > 255:
            image["pixels"][i] = 255
        image["pixels"][i] = round(image["pixels"][i])
    return image


def box_blur_maker(n):
    # creates a kernel with n x n dimensions within which all the values add to 1
    value = 1 / (n * n)
    n_list = [[value] * n] * n
    return n_list


# FILTERS


def blurred(image, kernel_size, sharpened=False):
    """
    Return a new image representing the result of applying a box blur (with the
    given kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)

    # then compute the correlation of the input image with that kernel

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    kernel = box_blur_maker(kernel_size)
    new_image = correlate(image, kernel, boundary_behavior="extend")
    if sharpened == True:
        return new_image
    checked_image = round_and_clip_image(new_image)
    return checked_image


def sharpened(image, n):
    """
    Return a new image that represents a sharpened version of the given image.
    This will be done by creating a blurry version of the image (through blurred function)
    and using a formula of S = 2 * I - B for each pixel position. Make sure the image
    pixels are rounded and within a range between 0 and 255.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # use blurred function to create a blurry image
    sharpened_image = image.copy()
    sharpened_image["pixels"] = image["pixels"].copy()
    blurry_image = blurred(image, n, sharpened=True)
    # apply formula to every pixel position using a copy of original image and also the blurred image
    for r in range(image["height"]):
        for c in range(image["width"]):
            new_color = 2 * get_pixel(image, r, c) - get_pixel(blurry_image, r, c)
            set_pixel(sharpened_image, r, c, new_color)
    return round_and_clip_image(sharpened_image)


def edges(image):
    """
    Return a new image through this function that takes in two kernels (and sets boundary
    behavior to "extend") and uses correlate to create to new images. Then, take the square root of the
    corresponding pixels squared and added together (sort of like distance method). This will create an
    image where the edges are emphasized. Make sure the image pixels are rounded and within a range
    between 0 and 255.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # use correlate to create two new images, each with separate kernels.
    edges_image = image.copy()
    edges_image["pixels"] = image["pixels"].copy()
    k1 = [
        [-1, -2, -1],
        [
            0,
            0,
            0,
        ],
        [1, 2, 1],
    ]
    k2 = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    image1 = correlate(image, k1, "extend")
    image2 = correlate(image, k2, "extend")
    # apply formula to every pixel position in the list
    for r in range(image["height"]):
        for c in range(image["width"]):
            new_color = (
                get_pixel(image1, r, c) ** 2 + (get_pixel(image2, r, c) ** 2)
            ) ** (1 / 2)
            set_pixel(edges_image, r, c, new_color)
    return round_and_clip_image(edges_image)


# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image("test_images/cat.png")
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [
                round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in img_data
            ]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError(f"Unsupported image mode: {img.mode}")
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the "mode" parameter.
    """
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place fors
    # generating images, etc.

    # bluegill = load_greyscale_image("test_images/bluegill.png")
    # inverted_bluegill = inverted(bluegill)
    # save_greyscale_image(inverted_bluegill, "inverted_bluegill.png", mode="PNG")

    kernel = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    # pigbird = load_greyscale_image("test_images/pigbird.png")
    # pigbird_zero = correlate(pigbird, kernel, "zero")
    # save_greyscale_image(pigbird_zero, "pigbird_zero.png", mode="PNG")

    # pigbird = load_greyscale_image("test_images/pigbird.png")
    # pigbird_extend = correlate(pigbird, kernel, "extend")
    # save_greyscale_image(pigbird_extend, "pigbird_extend.png", mode="PNG")

    # pigbird = load_greyscale_image("test_images/pigbird.png")
    # pigbird_wrap = correlate(pigbird, kernel, "wrap")
    # save_greyscale_image(pigbird_wrap, "pigbird_wrap.png", mode="PNG")

    # cat = load_greyscale_image("test_images/cat.png")
    # cat_extend = blurred(cat, 13)
    # save_greyscale_image(cat_extend, "cat_extend.png", mode="PNG")

    # cat = load_greyscale_image("test_images/cat.png")
    # cat_zero = blurred(cat, 13)
    # save_greyscale_image(cat_zero, "cat_zero.png", mode="PNG")

    # cat = load_greyscale_image("test_images/cat.png")
    # cat_wrap = blurred(cat, 13)
    # save_greyscale_image(cat_wrap, "cat_wrap.png", mode="PNG")

    # python = load_greyscale_image("test_images/python.png")
    # python_sharpened = sharpened(python,11)
    # save_greyscale_image(python_sharpened, "python_sharpened.png", mode="PNG")

    # construct = load_greyscale_image("test_images/construct.png")
    # construct_edges = edges(construct)
    # save_greyscale_image(construct_edges, "construct_edges.png", mode="PNG")s
