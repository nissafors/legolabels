from PIL import Image, ImageDraw
import numpy as np

class NotAvailableError(Exception):
    pass

class NoImagesError(Exception):
    pass

class Label:
    """Label composed of horizontally or vertically stacked images.

    Usage:
        Init a new HLabel. Then add images using add_image() and create the label using make().
        After make(), calls to show(), get_img() and save() will be valid.
    
    Args:
        width_mm (int): Label width in mm. Must be larger than height_mm.
        height_mm (int): Label height in mm. Must be smaller than width_mm.
        margins_mm (dict): Label margins in mm. Valid keys are 'top', 'bottom', 'left' and 'right'.
        spacing_mm (int): Spacing between images in mm.
        dpi (int): Label resolution in dots per inch.
        dot_size_mm (int|float): Dot diameter in mm in the overflow dot-dot-dot image.
    """
    def __init__(self, width_mm, height_mm, margins_mm={'top': 0, 'bottom': 0, 'left': 0, 'right': 0}, spacing_mm=0, dpi=300, dot_size_mm=2):
        self._is_vertical = height_mm > width_mm
        if self._is_vertical:
            width_mm, height_mm = height_mm, width_mm
        self._dpi = dpi
        self._px = self._to_px(width_mm), self._to_px(height_mm)
        self._img = Image.new(mode='RGB', size=self._px, color=(0xFF, 0xFF, 0xFF, 0xFF))
        self._images = []
        self._dot_size = self._to_px(dot_size_mm)
        self._is_made = False
        self.set_margins(margins_mm)
        self.set_spacing(spacing_mm)

    def add_image(self, img):
        """Add an image to the label.
        
        Args:
            img (PIL.Image.Image): The image to add.
        """
        rgb = img.convert('RGB')
        if self._is_vertical:
            rgb = rgb.transpose(Image.ROTATE_90)
        self._images.append(rgb)

    def make(self):
        """Make label by scaling and laying out images on the label surface."""
        if len(self._images) == 0:
            raise NoImagesError()
        max_width = self._box[1][0] - self._box[0][0]
        max_height = self._box[1][1] - self._box[0][1]
        scale_factors = [self._scale_factor(x.height, max_height) for x in self._images]
        
        num_full_imgs = self._fit_count(scale_factors, max_width)
        images = self._images[:num_full_imgs]
        total_scaled_width = self._total_scaled_width(images, scale_factors)
        if num_full_imgs < len(self._images):
            images.append(self._dotdotdot_img())
            total_scaled_width = self._total_scaled_width(images, scale_factors)
            scale_factors[num_full_imgs] = 1
            while(total_scaled_width > max_width):
                images.pop(len(images) - 2)
                scale_factors[len(images) - 1] = 1
                total_scaled_width = self._total_scaled_width(images, scale_factors)
        pos = int(max_width / 2 - total_scaled_width / 2) + self._box[0][0], self._box[0][1]
        
        for i, image in enumerate(images):
            new_size = (int(image.width * scale_factors[i]), int(image.height * scale_factors[i]))
            self._img.paste(image.resize(new_size), pos)
            pos = (pos[0] + new_size[0] + self._spacing, pos[1])
        self._is_made = True

    def show(self):
        """Preview label using PIL.Image.Image.show()."""
        self._guard_not_made()
        img = self._img
        if self._is_vertical:
            img = img.transpose(Image.ROTATE_270)
        img.show()

    def set_spacing(self, spacing_mm):
        """Set spacing between images.
        
        Args:
            spacing_mm (int): Spacing in mm.
        """
        self._spacing = self._to_px(spacing_mm)

    def set_margins(self, margins_mm):
        """Set margins around label edges.
        
        Args:
            margins_mm (dict): Label margins in mm. Valid keys are 'top', 'bottom', 'left' and 'right'.
        """
        self._box = (self._to_px(margins_mm['left']), self._to_px(margins_mm['top'])), (self._px[0] - self._to_px(margins_mm['right']), self._px[1] - self._to_px(margins_mm['bottom']))

    def get_img(self):
        """Get an image representation of the label.
        
        Returns:
            PIL.Image.Image: The label as a PIL Image object.
        """
        self._guard_not_made()
        img = self._img.transpose(Image.ROTATE_270) if self._is_vertical else self._img.copy()
        return img

    def _to_px(self, mm):
        """Convert from mm to px."""
        return int(round(self._dpi * mm / 25.4))

    def _scale_factor(self, actual, scaled):
        """Calculate scale factor."""
        return scaled / actual

    def _fit_count(self, scale_factors, width):
        """Return number of images that fit within width."""
        for i, img in enumerate(self._images):
            width -= img.width * scale_factors[i]
            if width <= 0:
                return i
            width -= self._spacing
        return len(self._images)

    def _total_scaled_width(self, images, scale_factors):
        """Caclucale total scaled width for images with corresponding scale_factors."""
        return sum([int(x.width * scale_factors[i]) for i, x in enumerate(images)]) + self._spacing * (len(images) - 1)

    def _dotdotdot_img(self):
        """Return the overflow dot-dot-dot image."""
        img = Image.new('RGB', (self._dot_size * 4 + 1, self._dot_size + 1), (0xFF, 0xFF, 0xFF))
        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 0, self._dot_size, self._dot_size), fill=(0, 0, 0), outline=(0, 0, 0))
        draw.ellipse((int(self._dot_size * 1.5), 0, int(self._dot_size * 2.5), self._dot_size), fill=(0, 0, 0), outline=(0, 0, 0))
        draw.ellipse((self._dot_size * 3, 0, self._dot_size * 4, self._dot_size), fill=(0, 0, 0), outline=(0, 0, 0))
        width = self._dot_size * 4 + 1
        if self._is_vertical:
            img = img.transpose(Image.ROTATE_90)
            width = self._dot_size + 1
        base = Image.new('RGB', (width, self._box[1][1] - self._box[0][1]), (0xFF, 0xFF, 0xFF))
        base.paste(img, (0, int(base.height // 2 - img.height // 2)))
        return base

    def _guard_not_made(self):
        """Raise exception if make() has not been called."""
        if not self._is_made:
            raise NotAvailableError()


if __name__ == "__main__":
    from rebrickable import Part, PartImage
    api_key = "b588880dae6f8e2a9bdaf92efee7f58a"
    rp = Part(api_key)
    img_path = rp.get_img("54200")
    if (img_path == ''):
        exit(1)
    pi = PartImage(img_path)
    pi.crop()
    l = Label(65, 25, margins_mm={'top': 2, 'bottom': 2, 'left': 4, 'right': 4}, dot_size_mm=1.5)
    l.add_image(pi.img)
    l.add_image(pi.img)
    l.add_image(pi.img)
    l.set_spacing(2)
    l.make()
    l.show()
