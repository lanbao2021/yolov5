import os

if __name__ == '__main__':
    filename = 'runs/detect/exp20'
    for i, j, images in os.walk('./' + filename):
        print(i, j, images)

