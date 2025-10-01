class ImagesModel:
    def __init__(self):
        self.images = []

    def add_image(self, image):
        self.images.append(image)

    def get_images(self):
        return self.images