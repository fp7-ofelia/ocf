from foam.sfa.rspecs.elements.element import Element
from foam.sfa.rspecs.elements.disk_image import DiskImage

class PGv2DiskImage:

    @staticmethod
    def add_images(xml, images):
        if not images:
            return 
        if not isinstance(images, list):
            images = [images]
        for image in images: 
            xml.add_instance('disk_image', image, DiskImage.fields)
    
    @staticmethod
    def get_images(xml, filter={}):
        xpath = './default:disk_image | ./disk_image'
        image_elems = xml.xpath(xpath)
        images = []
        for image_elem in image_elems:
            image = DiskImage(image_elem.attrib, image_elem)
            images.append(image)
        return images

