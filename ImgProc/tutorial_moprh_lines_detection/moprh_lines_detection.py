import numpy as np
import sys
import cv2

def main(argv):
    if len(argv) < 1:
        print 'Not enough parameters'
        print 'Usage:\nmoprh_lines_detection.py < path_to_image >'
        return -1

    # [load_image]
    src = cv2.imread(argv[1], cv2.IMREAD_COLOR)
    if src is None:
        print 'Can\'t read the image'
        return -1

    # Show source image
    cv2.imshow("src", src)
    # [load_image]

    # [gray]
    # Transform source image to gray if it is not
    if len(src.shape) != 2:
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    else:
        gray = src

    # Show gray image
    cv2.imshow("gray", gray)
    # [gray]

    # [bin]
    # Apply adaptiveThreshold at the bitwise_not of gray, notice the ~ symbol
    gray = cv2.bitwise_not(gray)
    bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, \
                                cv2.THRESH_BINARY, 15, -2)
    # Show binary image
    cv2.imshow("binary", bw)
    # [bin]

    # [init]
    # Create the images that will use to extract the horizontal and vertical lines
    horizontal = np.copy(bw)
    vertical = np.copy(bw)
    # [init]

    # [horiz]
    # Specify size on horizontal axis
    cols = horizontal.shape[1]
    horizontalsize = cols / 30

    # Create structure element for extracting horizontal lines through morphology operations
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalsize, 1))

    # Apply morphology operations
    horizontal = cv2.erode(horizontal, horizontalStructure)
    horizontal = cv2.dilate(horizontal, horizontalStructure)

    # Show extracted horizontal lines
    cv2.imshow("horizontal", horizontal)
    # [horiz]

    # [vert]
    # Specify size on vertical axis
    rows = vertical.shape[0]
    verticalsize = rows / 30

    # Create structure element for extracting vertical lines through morphology operations
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))

    # Apply morphology operations
    vertical = cv2.erode(vertical, verticalStructure)
    vertical = cv2.dilate(vertical, verticalStructure)

    # Show extracted vertical lines
    cv2.imshow("vertical", vertical)
    # [vert]

    # [smooth]
    # Inverse vertical image
    vertical = cv2.bitwise_not(vertical)
    cv2.imshow("vertical_bit", vertical)

    '''
    Extract edges and smooth image according to the logic
    1. extract edges
    2. dilate(edges)
    3. src.copyTo(smooth)
    4. blur smooth img
    5. smooth.copyTo(src, edges)
    '''

    # Step 1
    edges = cv2.adaptiveThreshold(vertical, 255, cv2.ADAPTIVE_THRESH_MEAN_C, \
                                cv2.THRESH_BINARY, 3, -2)
    cv2.imshow("edges", edges)

    # Step 2
    kernel = np.ones((2, 2), np.uint8)
    edges = cv2.dilate(edges, kernel)
    cv2.imshow("dilate", edges)

    # Step 3
    smooth = np.copy(vertical)

    # Step 4
    smooth = cv2.blur(smooth, (2, 2))

    # Step 5
    (rows, cols) = np.where(edges != 0)
    vertical[rows, cols] = smooth[rows, cols]

    # Show final result
    cv2.imshow("smooth", vertical)
    # [smooth]

    cv2.waitKey(0)
    return 0

if __name__ == "__main__":
    main(sys.argv)

