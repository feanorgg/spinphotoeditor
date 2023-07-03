from rembg import remove, new_session
from PIL import Image

input_path = './test/9 апреля раскладка0509.jpg'
output_path = 'test_out/6.jpg'

rsession = new_session(
    "u2net"
)


def process(session, image, *, size=None, bgcolor='#f6f6f6'):
    if size is not None:
        image = image.resize(size)
    else:
        size = image.size
    result = Image.new("RGB", size, bgcolor)
    out = remove(image, session=session, alpha_matting=True, alpha_matting_erode_size=15)
    result.paste(out, mask=out)
    return result


img = Image.open(input_path)
res = process(rsession, img, size=img.size, bgcolor="#F6F6F6")  # bgcolor="#F6F6F6")
res.save(output_path)
