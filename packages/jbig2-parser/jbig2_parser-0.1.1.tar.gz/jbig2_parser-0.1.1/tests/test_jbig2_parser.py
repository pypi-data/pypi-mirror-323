import jbig2_parser
import structlog
from PIL import Image
from io import BytesIO

logger = structlog.get_logger()

def test_jbig2_parser():

    test_image_path = r"tests\test_images\text.jb2" 

    with open(test_image_path, "rb") as file:
        jbig2_test_data = file.read()

    try:
        png_buffer = jbig2_parser.parse_jbig2(jbig2_test_data)
        logger.info("JBIG2 decoding successful.")

        png_bytes = bytes(png_buffer)

        image = Image.open(BytesIO(png_bytes))
        logger.info(f"Decoded Image: {image.size}, Mode: {image.mode}")
        image.show()
    except RuntimeError as exc:
        logger.error(f"Error decoding JBIG2: {exc}")

if __name__ == "__main__":
    test_jbig2_parser()
