# Display Image

Display image is a Python project which provides a command `display-image` to visualize the image and metadata by QtPy6.
~~~~~~~~~~~~~~~{.shell}
display-image -i <path_to_image>
~~~~~~~~~~~~~~~
![displaye-image GUI](https://github.com/sygslhy/display-image/blob/master/images/display-image-gui.png)


| Image format  | Read | EXIF | Pixel precision        | Pixel type           | File extension                   |  Sidecar needed  |
|---------------|------|------|------------------------|----------------------|----------------------------------|------------------|
| BMP           | x    |      | 8 bits                 | Grayscale, RGB, RGBA | .bmp                             |                  |
| CFA           | x    |      | 16 bits                | Bayer                | .cfa                             |                  |
| DNG           | x    | x    | 16 bits                | Bayer, RGB           | .dng                             |                  |
| JPEG          | x    | x    | 8 bits                 | Grayscale, RGB       | .jpg, .jpeg                      |                  |
| MIPI RAW      | x    |      | 10 bits, 12 bits       | Bayer                | .RAWMIPI, .RAWMIPI10, .RAWMIPI12 | x                |
| PLAIN RAW     | x    |      | *                      | *                    | .raw .plain16, *                 | x                |
| PNG           | x    |      | 8 bits, 16 bits        | Grayscale, RGB, RGBA | .png                             |                  |
| TIFF          | x    | x    | 8 bits, 16 bits        | Bayer, RGB           | .tif, .tiff                      |                  |


# License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/sygslhy/display-image/blob/master/LICENSE.md) file for details.
