import cv2
import numpy as np
from ultralytics import YOLO
import time
from PIL import Image, ImageDraw, ImageFont


# tf.debugging.set_log_device_placement(True)
def main():
    vidcap = cv2.VideoCapture('videos/test.mp4')
    success, image = vidcap.read()
    # model = load_model('model.h5')
    model = YOLO("yolov8n.pt")
    names = model.names
    width, height, _ = image.shape
    frameSize = (height, width)
    frames = []
    new_frames = []
    framerate = 30
    # 0x31637661
    out = cv2.VideoWriter('output_video.mp4', 0x7634706d, framerate, frameSize)

    meta_data = 'out_video_meta.txt'
    file = open(meta_data, "w+")  # reads file to append

    while success:
        success, frame = vidcap.read()
        frames.append(frame)

    batch_size = 200
    tic = time.perf_counter()
    # frames = frames[499:500]
    for i in range(0, len(frames), batch_size):
        end_slice = i + batch_size if i + batch_size < len(frames) else len(frames) - 1
        frame_slice = frames[i: end_slice]
        results = model.predict(frame_slice)
        new_frames.extend(draw_boxes(frame_slice, results, names))
        for j in range(len(frame_slice)):
            # write classifications in file
            result = results[j].boxes
            v_scores = result.conf
            v_class = result.cls
            frame_time = (i + j) // framerate  # this is in seconds
            frame_time = frame_time * 1000  # convert to milliseconds (ms)
            items = [str(frame_time)]
            classes = set()
            thresh = 0.6
            for k in range(len(v_scores)):
                score = v_scores[k].item()
                if score >= thresh:
                    classes.add(names[v_class[k].item()])
            classes = list(classes)
            items.extend(classes)
            file.write(" ".join(items))
            file.write('\n')

            out.write(frame_slice[j])
    toc = time.perf_counter()

    print(f"Total Time: {toc - tic:0.4f} seconds")
    out.release()
    vidcap.release()
    file.close()


def draw_boxes(images, results, v_labels):
    new_images = []
    for j in range(len(images)):
        thresh = 0.6
        result = results[j].boxes
        v_boxes = result.xyxy
        v_scores = result.conf
        v_class = result.cls
        image = Image.fromarray(images[j])
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial.ttf", 15)
        for i in range(len(v_boxes)):
            score = v_scores[i].item()
            if score >= thresh:
                box = v_boxes[i]
                # get coordinates
                x1, y1, x2, y2 = box
                x1, y1, x2, y2 = x1.item(), y1.item(), x2.item(), y2.item()
                end_point = (x2, y2)
                start_point = (x1, y1)
                # draw the box
                draw.rectangle((start_point, end_point), outline="blue")
                # draw text and score in top left corner
                label = "%s (%.3f)" % (v_labels[v_class[i].item()], score)
                draw.text((x1, y1), label, (0, 0, 0), font=font)
        # image.show()
        new_images.append(np.array(image)[..., ::-1])
    return new_images

if __name__ == "__main__":
    main()
