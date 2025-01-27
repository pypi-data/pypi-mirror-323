import ddddocr

class Verifycode:

    @staticmethod
    def get_code(image):
        ocr = ddddocr.DdddOcr()
        result = ocr.classification(image)
        return result