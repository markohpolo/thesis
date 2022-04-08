import cv2
from os import walk
from os import mkdir

def export_frames(object_name: str, frame_limit: int):
    vidcap = cv2.VideoCapture('3d_models/{}.webm'.format(object_name))
    success,image = vidcap.read()
    count = 0
    mkdir("frames/{}".format(object_name))
    print("Exporting frames from {} ...".format(object_name))
    while success and count < frame_limit:
        count += 1
        cv2.imwrite("frames/{}/{}%d.png".format(object_name, object_name) % count, image)
        count += 1
        cv2.imwrite("frames/{}/{}%d.png".format(object_name, object_name) % count, cv2.flip(image, 1))
        success,image = vidcap.read()
    print("{} frames of {} captured".format(count - 1, object_name))

def export_original_frame(object_name, counter, image):
    cv2.imwrite("frames/{}_%d.png".format(object_name) % counter, image)

def main():
    _, _, object_names = next(walk("./3d_models"), (None, None, []))

    for object_name in object_names:
        export_frames(object_name[:-5], 2000)

if __name__ == "__main__":
    main()






