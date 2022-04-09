import cv2
from cv2 import normalize
import tqdm
import concurrent.futures
from os import walk

OBJECT = "vayne_run" # object name
OBJECT_ID = 0 # object id

NUM_WORKERS = 50
BACKGROUND = [58, 246, 142] # GREEN
TOLERANCE = 25
TOLERANCE_OFFSET_1_MIN = BACKGROUND[0] - 1.0 * TOLERANCE
TOLERANCE_OFFSET_1_MAX = BACKGROUND[0] + 1.0 * TOLERANCE
TOLERANCE_OFFSET_2_MIN = BACKGROUND[1] - 1.0 * TOLERANCE
TOLERANCE_OFFSET_2_MAX = BACKGROUND[1] + 1.0 * TOLERANCE
TOLERANCE_OFFSET_3_MIN = BACKGROUND[2] - 2.5 * TOLERANCE # Teemo viewer: 2.5
TOLERANCE_OFFSET_3_MAX = BACKGROUND[2] + 2.5 * TOLERANCE

def run_worker(frame_file):
    original_image = cv2.imread("frames/{}/{}".format(OBJECT, frame_file))
    rotate_1 = cv2.rotate(original_image, cv2.cv2.ROTATE_90_CLOCKWISE)

    image_length = len(original_image[0])
    image_width = len(original_image)

    top_y, bottom_y = get_coordinates(original_image, image_width // 2, image_width)
    left_x, right_x =  get_coordinates(rotate_1, image_length // 2, image_length)

    # with open("annotations/" + frame_file.replace("png", "txt"), 'w') as f:
    # #with open(frame_file.replace("png", "txt"), 'w') as f:
    #     f.write(normalize_frames(left_x, right_x, top_y, bottom_y, image_width, image_length))

    return left_x, right_x, top_y, bottom_y

def normalize_frames(left_x, right_x, top_y, bottom_y, image_width, image_length):
    b_width    = (right_x - left_x)
    b_height   = (bottom_y - top_y)
    b_center_x = b_width / 2 + left_x
    b_center_y = b_height / 2 + top_y
    
    # Normalise the co-ordinates by the dimensions of the image
    b_center_x /= image_length 
    b_center_y /= image_width 
    b_width    /= image_length 
    b_height   /= image_width
                
    return "{} {} {} {} {}".format(OBJECT_ID, round(b_center_x, 6), round(b_center_y, 6), round(b_width, 6), round(b_height, 6))

def is_pixel_green(pixel):
    if pixel[0] > TOLERANCE_OFFSET_1_MIN and pixel[0] < TOLERANCE_OFFSET_1_MAX \
        and pixel[1] > TOLERANCE_OFFSET_2_MIN and pixel[1] < TOLERANCE_OFFSET_2_MAX \
        and pixel[2] > TOLERANCE_OFFSET_3_MIN and pixel[2] < TOLERANCE_OFFSET_3_MAX:
        return True

    return False

def get_coordinates(image, center, bottom_limit):
    top = 0
    bottom = 0
    # center -> top
    for i in range(center, 0, -1):
        if all(is_pixel_green(pixel) for pixel in image[i]):
            top = i
            break
    # center -> bottom
    for i in range(center, bottom_limit):
        if all(is_pixel_green(pixel) for pixel in image[i]):
            bottom = i
            break

    return top, bottom
    
    

if __name__ == "__main__":
    _, _, frame_files = next(walk("./frames/{}".format(OBJECT)), (None, None, []))
    # scan frames
    # with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
    #     for left_x, right_x, top_y, bottom_y in tqdm.tqdm(executor.map(run_worker, frame_files), "Drawing boxes for {}".format(OBJECT), total=len(frame_files)):
    #         continue
            
    # sanity check code
    for frame_file in frame_files:
        if frame_file != "vayne_run2000.png":
            continue
        original_image = cv2.imread("frames/{}/{}".format(OBJECT, frame_file))
        left_x, right_x, top_y, bottom_y = run_worker(frame_file)
        image_with_box = cv2.rectangle(original_image, (left_x, top_y), (right_x, bottom_y), (255, 0, 0), 2)
        cv2.imwrite("{}_boxed.png".format(OBJECT), image_with_box)
        print(left_x, right_x, top_y, bottom_y)
