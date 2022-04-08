import cv2
import tqdm
import concurrent.futures
from os import walk

NUM_WORKERS = 50
BACKGROUND = [58, 246, 142] # GREEN
TOLERANCE = 25
TOLERANCE_OFFSET_1_MIN = BACKGROUND[0] - 1.0 * TOLERANCE
TOLERANCE_OFFSET_1_MAX = BACKGROUND[0] + 1.0 * TOLERANCE
TOLERANCE_OFFSET_2_MIN = BACKGROUND[1] - 1.0 * TOLERANCE
TOLERANCE_OFFSET_2_MAX = BACKGROUND[1] + 1.0 * TOLERANCE
TOLERANCE_OFFSET_3_MIN = BACKGROUND[2] - 2.5 * TOLERANCE # Teemo viewer: 2.5
TOLERANCE_OFFSET_3_MAX = BACKGROUND[2] + 2.5 * TOLERANCE

# BLACK_OFFSET_1_MIN = 0
# BLACK_OFFSET_1_MAX = 0 + 1.0 * TOLERANCE
# BLACK_OFFSET_2_MIN = 0
# BLACK_OFFSET_2_MAX = 0 + 1.0 * TOLERANCE
# BLACK_OFFSET_3_MIN = 0
# BLACK_OFFSET_3_MAX = 0 + 2.5 * TOLERANCE

# WHITE_OFFSET_1_MIN = 255 - 1.0 * TOLERANCE
# WHITE_OFFSET_1_MAX = 255
# WHITE_OFFSET_2_MIN = 255 - 1.0 * TOLERANCE
# WHITE_OFFSET_2_MAX = 255
# WHITE_OFFSET_3_MIN = 255 - 2.5 * TOLERANCE
# WHITE_OFFSET_3_MAX = 255


# def is_mouse_pixel(pixel):
#     if pixel[0] > WHITE_OFFSET_1_MIN and pixel[0] < WHITE_OFFSET_1_MAX \
#         and pixel[1] > WHITE_OFFSET_2_MIN and pixel[1] < WHITE_OFFSET_2_MAX \
#         and pixel[2] > WHITE_OFFSET_3_MIN and pixel[2] < WHITE_OFFSET_3_MAX:
#         return True

#     elif pixel[0] > BLACK_OFFSET_1_MIN and pixel[0] < BLACK_OFFSET_1_MAX \
#         and pixel[1] > BLACK_OFFSET_2_MIN and pixel[1] < BLACK_OFFSET_2_MAX \
#         and pixel[2] > BLACK_OFFSET_3_MIN and pixel[2] < BLACK_OFFSET_3_MAX:
#         return True

#     return False

def pixel_not_green(pixel):
    if not(pixel[0] > TOLERANCE_OFFSET_1_MIN and pixel[0] < TOLERANCE_OFFSET_1_MAX \
        and pixel[1] > TOLERANCE_OFFSET_2_MIN and pixel[1] < TOLERANCE_OFFSET_2_MAX \
        and pixel[2] > TOLERANCE_OFFSET_3_MIN and pixel[2] < TOLERANCE_OFFSET_3_MAX):
        return True

    return False

def run_worker(frame_file):
    original_image = cv2.imread("frames/vayne_run/{}".format(frame_file))
    rotate_1 = cv2.rotate(original_image, cv2.cv2.ROTATE_90_CLOCKWISE)
    rotate_2 = cv2.rotate(rotate_1, cv2.cv2.ROTATE_90_CLOCKWISE)
    rotate_3 = cv2.rotate(rotate_2, cv2.cv2.ROTATE_90_CLOCKWISE)

    image_length = len(original_image[0])
    image_width = len(original_image)

    top_y = get_coordinate(original_image)
    left_x =  get_coordinate(rotate_1)
    bottom_y = image_width - get_coordinate(rotate_2)
    right_x= image_length - get_coordinate(rotate_3)

    # sanity check code
    # image_with_box = cv2.rectangle(original_image, (left_x, top_y), (right_x, bottom_y), (255, 0, 0), 2)
    # cv2.imwrite("{}_boxed.png".format(frame_file), image_with_box)
    with open("annotations/" + frame_file.replace("png", "txt"), 'w') as f:
        f.write(str(left_x) + " ")
        f.write(str(right_x) + " ")
        f.write(str(top_y) + " ")
        f.write(str(bottom_y))

    return left_x, right_x, top_y, bottom_y


def get_coordinate(image):
    count = 0
    for i in range(len(image)):
        count += 1
        if count < 100:
            continue
        for pixel in image[i]:
            # if is_mouse_pixel(pixel):
            #     continue
            if pixel_not_green(pixel):
                return i                
    # 0 on fail
    return 0
    
    

if __name__ == "__main__":
    # scan all objects
    _, _, object_names = next(walk("./3d_models"), (None, None, []))
    for object_name in object_names:
        object_name = object_name[:-5]
        if object_name != "vayne_run":
            continue
        _, _, frame_files = next(walk("./frames/{}".format(object_name)), (None, None, []))
        # scan frames
        with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
            for left_x, right_x, top_y, bottom_y in tqdm.tqdm(executor.map(run_worker, frame_files), "Drawing boxes for {}".format(object_name), total=len(frame_files)):
                continue
                
        # for frame_file in frame_files:
        #     if frame_file != "vayne_run1.png":
        #         continue
        #     left_x, right_x, top_y, bottom_y = run_worker(frame_file)
        #     print(left_x, right_x, top_y, bottom_y)
