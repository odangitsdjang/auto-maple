import numpy as np
import cv2
import matplotlib.pyplot as plt

TEST_FRAME = cv2.imread('assets/image_2a.jpg', 1)
TEST_TEMPLATE = cv2.imread('assets/image2b.jpg', 0)

def multi_match(frame, template, threshold=0.95,save_result = False):
    """
    Finds all matches in FRAME that are similar to TEMPLATE by at least THRESHOLD.
    :param frame:       The image in which to search.
    :param template:    The template to match with.
    :param threshold:   The minimum percentage of TEMPLATE that each result must match.
    :return:            An array of matches that exceed THRESHOLD.
    """

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))
    results = []
    if save_result:
        img_disp = gray.copy()
    for p in locations:
        x = int(round(p[0] + template.shape[1] / 2))
        y = int(round(p[1] + template.shape[0] / 2))
        results.append((x, y))
        if save_result:
            right_bottom = (p[0] + template.shape[1], p[1] + template.shape[0])
            cv2.rectangle(img_disp, p,right_bottom, (0,255,0), 5, 8, 0 )
    if save_result:
        fig,ax = plt.subplots(3,1)
        fig.suptitle('match_template')
        ax[0].set_title('img_src')
        ax[0].imshow(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)) 
        ax[1].set_title('img_templ')
        ax[1].imshow(template,'gray') 
        ax[2].set_title('img_disp')
        ax[2].imshow(cv2.cvtColor(img_disp,cv2.COLOR_BGR2RGB)) 
        plt.savefig('plot.png') 
        plt.show()   
    return results

# RUNE_BUFF_TEMPLATE = cv2.imread('assets/rune_buff_template.jpg', 0)
# frame = cv2.imread('test_rune_2.PNG', 1)
# r = multi_match(frame[:35, :],RUNE_BUFF_TEMPLATE,0.93,save_result=True)

# template should be the smaller sized of the two, set the vars appropriately
print(len(TEST_TEMPLATE))
print(len(TEST_FRAME))

multi_match(TEST_FRAME,TEST_TEMPLATE, threshold=0.47,save_result=True)