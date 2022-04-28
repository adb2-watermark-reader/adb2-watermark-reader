import time

import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    width = 1280
    height = 720

    cap = cv.cv2.VideoCapture('video.ts')
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            first_row_luma = cv.cvtColor(frame, cv.COLOR_BGR2YCR_CB)[0, :, 0][None]
            resized = cv.resize(first_row_luma, (30 * 8, 1))

            np.set_printoptions(threshold=np.inf)
            print(resized)
            print(np.any(np.logical_and(resized > 5, resized < 7)))
            print(first_row_luma)

            print(first_row_luma.max())

            bins = np.arange(resized.min(), resized.max() + 1, 1)
            print(bins)

            plt.hist(resized[0, :], bins=bins)
            plt.show()

            print("hmm")

            scaled_luma = np.repeat(first_row_luma, height, axis=0)
            rescaled_luma = np.repeat(resized, height, axis=0)

            cv.imshow("hmm", scaled_luma)
            cv.waitKey(0)
            cv.imshow("hmm", rescaled_luma)
            cv.waitKey(0)
