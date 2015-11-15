from __future__ import absolute_import

from willow.image import (
    Image,
    JPEGImageFile,
    PNGImageFile,
    GIFImageFile,
    RGBImageBuffer,
    RGBAImageBuffer,
)


def _PIL_Image():
    import PIL.Image
    return PIL.Image


class PillowImage(Image):
    def __init__(self, image):
        self.image = image

    @classmethod
    def check(cls):
        _PIL_Image()

    @Image.operation
    def get_size(self):
        return self.image.size

    @Image.operation
    def has_alpha(self):
        img = self.image
        return img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)

    @Image.operation
    def has_animation(self):
        # Animation is not supported by PIL
        return False

    @Image.operation
    def resize(self, size):
        if self.image.mode in ['1', 'P']:
            image = self.image.convert('RGB')
        else:
            image = self.image

        image = image.resize(size, _PIL_Image().ANTIALIAS)

        return PillowImage(image)

    @Image.operation
    def crop(self, rect):
        return PillowImage(self.image.crop(rect))

    @Image.operation
    def save_as_jpeg(self, f, quality=85):
        if self.image.mode in ['1', 'P']:
            image = self.image.convert('RGB')
        else:
            image = self.image

        image.save(f, 'JPEG', quality=quality)

    @Image.operation
    def save_as_png(self, f):
        self.image.save(f, 'PNG')

    @Image.operation
    def save_as_gif(self, f):
        if 'transparency' in self.image.info:
            self.image.save(f, 'GIF', transparency=self.image.info['transparency'])
        else:
            self.image.save(f, 'GIF')

    @classmethod
    @Image.converter_from(JPEGImageFile)
    @Image.converter_from(PNGImageFile)
    @Image.converter_from(GIFImageFile, cost=200)
    def open(cls, image_file):
        image_file.f.seek(0)
        image = _PIL_Image().open(image_file.f)
        image.load()
        return cls(image)

    @Image.converter_to(RGBImageBuffer)
    def to_buffer_rgb(self):
        image = self.image

        if image.mode != 'RGB':
            image = image.convert('RGB')

        return RGBImageBuffer(image.size, image.tobytes())

    @Image.converter_to(RGBAImageBuffer)
    def to_buffer_rgba(self):
        image = self.image

        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        return RGBAImageBuffer(image.size, image.tobytes())


willow_image_classes = [PillowImage]
