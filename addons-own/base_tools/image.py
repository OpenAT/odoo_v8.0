# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from PIL import Image
#from PIL import ImageEnhance
#from random import randint


def resize_to_thumbnail(img, box=(440, 440), fit=1):
    '''Downsample the image.
    @param img: Image - base64 Image Data
    @param box: tuple(x, y) - the bounding box of the result image
    @param fit: boolean - crop the image to fill the box
    '''
    # DECODE the img to an base64 PIL object
    img = Image.open(StringIO.StringIO(img.decode('base64')))
    filetype = img.format.upper()
    filetype = {'BMP': 'PNG', }.get(filetype, filetype)
    if img.mode not in ["1", "L", "P", "RGB", "RGBA"]:
        img = img.convert("RGB")

    # RESIZE
    #preresize image with factor 2, 4, 8 and fast algorithm
    factor = 1
    while img.size[0]/factor > 2*box[0] and img.size[1]*2/factor > 2*box[1]:
        factor *=2
    if factor > 1:
        img.thumbnail((img.size[0]/factor, img.size[1]/factor), Image.NEAREST)

    #calculate the cropping box and get the cropped part
    if fit:
        x1 = y1 = 0
        x2, y2 = img.size
        wRatio = 1.0 * x2/box[0]
        hRatio = 1.0 * y2/box[1]
        if hRatio > wRatio:
            y1 = int(y2/2-box[1]*wRatio/2)
            y2 = int(y2/2+box[1]*wRatio/2)
        else:
            x1 = int(x2/2-box[0]*hRatio/2)
            x2 = int(x2/2+box[0]*hRatio/2)
        img = img.crop((x1, y1, x2, y2))

    #Resize the image with best quality algorithm ANTI-ALIAS
    img.thumbnail(box, Image.ANTIALIAS)

    #RETURN the image
    background_stream = StringIO.StringIO()
    img.save(background_stream, filetype)
    return background_stream.getvalue().encode('base64')
