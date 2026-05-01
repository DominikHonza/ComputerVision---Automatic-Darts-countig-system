import cv2
import numpy as np
from warp import normalize_board


class DartDetector:

    def __init__(self, base_frame):

        self.base = base_frame
        self.base_gray = cv2.cvtColor(base_frame, cv2.COLOR_BGR2GRAY)
        self.base_gray = cv2.GaussianBlur(self.base_gray, (5,5), 0)


    def process(self, frame):

        output = frame.copy()

        test_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        test_gray = cv2.GaussianBlur(test_gray,(5,5),0)

        diff = cv2.absdiff(self.base_gray, test_gray)

        _, thresh = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)

        kernel = np.ones((5,5),np.uint8)
        thresh = cv2.dilate(thresh, kernel, iterations=2)

        contours,_ = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        darts = []
        
        for c in contours:

            area = cv2.contourArea(c)

            if area < 1200:
                continue

            x,y,w,h = cv2.boundingRect(c)

            cv2.rectangle(output,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.drawContours(output,[c],-1,(255,0,0),2)

            M = cv2.moments(c)

            if M["m00"] == 0:
                continue

            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            center = np.array([cx, cy])

            max_dist = 0
            tip = None

            for p in c:

                point = p[0]
                dist = np.linalg.norm(point - center)

                if dist > max_dist:
                    max_dist = dist
                    tip = point

            if tip is None:
                continue

            ring, sector, score = normalize_board(frame, tuple(tip))

            darts.append((ring, sector, score))

            if ring == "TRIPLE":
                label = f"T{sector}"
            elif ring == "DOUBLE":
                label = f"D{sector}"
            elif ring == "SINGLE":
                label = f"S{sector}"
            elif ring == "OUTER_BULL":
                label = "25"
            elif ring == "BULL":
                label = "50"
            else:
                label = "MISS"

            cv2.circle(output,(cx,cy),5,(0,255,255),-1)

            text_x = tip[0] - 20
            text_y = tip[1] - 20

            cv2.putText(
                output,
                label,
                (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0,255,255),
                2,
                cv2.LINE_AA
            )

            cv2.circle(output,tuple(tip),6,(0,0,255),-1)

            cv2.line(output,(cx,cy),tuple(tip),(0,255,255),3)

        return output, darts