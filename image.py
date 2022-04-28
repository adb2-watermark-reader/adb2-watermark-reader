import cv2 as cv
import numpy as np

if __name__ == "__main__":
    img = cv.imread("snapshot.png")

    first_row_luma = cv.cvtColor(img, cv.COLOR_BGR2YCR_CB)[0, :, 0].reshape((1, 1280))
    scaled_luma = np.repeat(first_row_luma, 720, axis=0)

    print(img[0, :, :].shape)

    cv.imshow("hmm", scaled_luma)
    cv.waitKey(0)