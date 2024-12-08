# Faisal Z. Qureshi
# www.vclab.ca

#Daniel Zajac - 100820183

import argparse
import PySimpleGUI as sg
from PIL import Image
from io import BytesIO
import numpy as np
import cv2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib
from scipy.stats import multivariate_normal
from scipy.ndimage import convolve
import math
import time
import yaml
import random
import scipy
from scipy.spatial.distance import cdist
matplotlib.use('TkAgg')

def gaussian_kernel(size, sigma=1):
    kernel = np.zeros((size, size), dtype=np.float32)
    center = (size - 1) / 2

    # Populate the kernel using the Gaussian formula
    for i in range(size):
        for j in range(size):
            x, y = i - center, j - center
            kernel[i, j] = np.exp(-(x**2 + y**2) / (2 * sigma**2))

    # Normalize the kernel so it sums to 1
    kernel /= np.sum(kernel)
    
    return kernel

def np_im_to_data(im):
    array = np.array(im, dtype=np.uint8)
    im = Image.fromarray(array)
    with BytesIO() as output:
        im.save(output, format='PNG')
        data = output.getvalue()
    return data

def draw_smooth_line(image, pt1, pt2, color, thickness):
    overlay = image.copy()
    cv2.line(overlay, pt1, pt2, color, thickness)
    alpha = 0.7  # Transparency factor
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

def display_image(np_image, width, height, filename):
    # Convert numpy array to data that sg.Graph can understand
    image_data = np_im_to_data(np_image)

    np_image2 = np.copy(np_image)

    # Define the layout
    layout = [
        [sg.Column([ #making columns because the text wasn't lining up without putting image and text in the same column
            [sg.Text('Original', font=('Arial', 16), justification='center', text_color='black')],
            [sg.Graph(
                canvas_size=(width, height),
                graph_bottom_left=(0, 0),
                graph_top_right=(width, height),
                key='-IMAGE-',
                background_color='white',
                change_submits=True,
                drag_submits=True)]
        ], element_justification='center'),

        sg.Column([
            [sg.Text('Result', font=('Arial', 16), justification='center', text_color='black')],
            [sg.Graph(
                canvas_size=(width, height),
                graph_bottom_left=(0, 0),
                graph_top_right=(width, height),
                key='-IMAGE2-',
                background_color='white',
                change_submits=True,
                drag_submits=True)]
        ], element_justification='center')],
    
        [sg.Text('Minimum line length'), sg.Slider(range=(1, 20), default_value=2, resolution=1.0, orientation='h', size=(40, 20), key='-MINLEN_SLIDER-'), sg.Button('Save settings'), sg.Button('Load settings')],
        [sg.Text('Maximum line length'), sg.Slider(range=(1, 20), default_value=5, resolution=1.0, orientation='h', size=(40, 20), key='-MAXLEN_SLIDER-'), sg.Button('Save image'), sg.Button('Load image')],
        [sg.Text('Minimum line width'), sg.Slider(range=(1, 15), default_value=2, resolution=1.0, orientation='h', size=(40, 20), key='-MINWID_SLIDER-'), sg.Text('Sobel half length'), sg.Slider(range=(1, 3), default_value=1, resolution=1.0, orientation='h', size=(40, 20), key='-SOBEL_SLIDER-')],
        [sg.Text('Maximum line width'), sg.Slider(range=(1, 15), default_value=5, resolution=1.0, orientation='h', size=(40, 20), key='-MAXWID_SLIDER-')],
        [sg.Text('Edge detection strength'), sg.Slider(range=(1, 255), default_value=53, resolution=1.0, orientation='h', size=(40, 20), key='-EDGE_DETECTION_STRENGTH_SLIDER-'), sg.Text('Allowed Error'), sg.Slider(range=(0, 150), default_value=16, resolution=1.0, orientation='h', size=(40, 20), key='-ERROR_SLIDER-')],
        [sg.Button('Apply filter'), sg.Push(), sg.Button('Quit')],
    ]

    # Create the window
    window = sg.Window('Display Image', layout, finalize=True)    
    window['-IMAGE-'].draw_image(data=image_data, location=(0, height))
    window['-IMAGE2-'].draw_image(data=image_data, location=(0, height))

    # Event loop
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Quit':
            break
        if event == 'Save settings':
            #formatting our slider data
            settings = {
            'minlen': values['-MINLEN_SLIDER-'],
            'maxlen': values['-MAXLEN_SLIDER-'],
            'minwid': values['-MINWID_SLIDER-'],
            'maxwid': values['-MAXWID_SLIDER-'],
            'edge': values['-EDGE_DETECTION_STRENGTH_SLIDER-']
            }

            #putting slider data into yaml file
            with open('settings.yaml', 'w') as file:
                yaml.dump(settings, file)
        
        if event == 'Load settings':
            #loading the yaml file into settings variable
            try:
                with open('settings.yaml', 'r') as file:
                    settings = yaml.load(file, Loader=yaml.FullLoader)
            except FileNotFoundError:
                #if user accidently loads without having saved settings, we make default file so that no error occurs
                print("Settings file did not exist, default one was created.")

                settings = {
                'minlen': 1,
                'maxlen': 40,
                'minwid': 1,
                'maxwid': 15,
                'edge': 100
                }

                with open('settings.yaml', 'w') as file:
                    yaml.dump(settings, file)

            #updating the current slider values with the loaded ones
            minlen =  settings['minlen']
            maxlen = settings['maxlen']
            minwid = settings['minwid']
            maxwid = settings['maxwid']
            edge = settings['edge']

            window['-MINLEN_SLIDER-'].update(minlen)
            window['-MAXLEN_SLIDER-'].update(maxlen)
            window['-MINWID_SLIDER-'].update(minwid)
            window['-MAXWID_SLIDER-'].update(maxwid)
            window['-EDGE_DETECTION_STRENGTH_SLIDER-'].update(edge)

        if event == 'Apply filter':

            x_sobel = np.array([
                [-1, 0, 1],
                [-2, 0, 2],
                [-1, 0, 1]
            ])
            y_sobel = np.array([
                [-1, -2, -1],
                [0, 0, 0],
                [1, 2, 1]
            ])
            # x_sobel = np.array([
            #     [-3, -2, -1, 0, 1, 2, 3],
            #     [-3, -2, -1, 0, 1, 2, 3],
            #     [-5, -4, -2, 0, 2, 4, 5],
            #     [-6, -5, -3, 0, 3, 5, 6],
            #     [-5, -4, -2, 0, 2, 4, 5],
            #     [-3, -2, -1, 0, 1, 2, 3],
            #     [-3, -2, -1, 0, 1, 2, 3]
            # ])
            # y_sobel = np.array([
            #     [3, 3, 5, 6, 5, 3, 3],
            #     [2, 2, 4, 5, 4, 2, 2],
            #     [1, 1, 2, 3, 2, 1, 1],
            #     [0, 0, 0, 0, 0, 0, 0],
            #     [-1, -1, -2, -3, -2, -1, -1],
            #     [-2, -2, -4, -5, -4, -2, -2],
            #     [-3, -3, -5, -6, -5, -3, -3]
            # ])

            #getting our variables set up for drawing lines in gradient directions
            if values['-MAXLEN_SLIDER-'] > values['-MINLEN_SLIDER-']:
                stroke_length_range = (values['-MINLEN_SLIDER-'], values['-MAXLEN_SLIDER-'])
            else:
                stroke_length_range = (values['-MAXLEN_SLIDER-'], values['-MINLEN_SLIDER-'])
            
            if values['-MAXWID_SLIDER-'] > values['-MINWID_SLIDER-']:
                stroke_width_range = (values['-MINWID_SLIDER-'], values['-MAXWID_SLIDER-'])
            else:
                stroke_width_range = (values['-MAXWID_SLIDER-'], values['-MINWID_SLIDER-'])
            edge_threshold = 255-values['-EDGE_DETECTION_STRENGTH_SLIDER-'] + 1
            error = values['-ERROR_SLIDER-']

            # edges = np.zeros_like(grad_mag, dtype=np.uint8)
            # edges[grad_mag > edge_threshold] = 1

            np_image2 = np.copy(np_image)
            np_image3 = np.full_like(np_image, np.iinfo(np_image2.dtype).max)

            brushes = [16, 8, 4, 2]
            for brush_radius in brushes:
                np_imageblur = cv2.bilateralFilter(np_image, (2*brush_radius)+1, 75, 75)
                np_imageblur = np.mean(np_imageblur, axis=2).astype(np.uint8) #for detecting edges using a mean grayscale version

                k = 1 #k is the halflength of sobel filter

                #initializing gradients as 0 to start for the edges which cannot be convolved at
                x_grad = np.zeros(np_imageblur.shape, dtype=np.int32)
                y_grad = np.zeros(np_imageblur.shape, dtype=np.int32)

                #applying the sobel filter to find the gradient at each pixel (exluding edge pixels)
                for i in range(k, np_image2.shape[0] - k):
                    for j in range(k, np_image2.shape[1] - k):
                        patch = np_imageblur[i-k:i+k+1, j-k:j+k+1]
                        x_grad[i, j] = np.sum(x_sobel * patch)
                        y_grad[i, j] = np.sum(y_sobel * patch)
                        # if i == 130 and j == 260:
                        #     print(patch)
                        #     print(x_grad[i, j])
                        #     print(y_grad[i, j])
                        #     print(np.arctan2(y_grad[i, j], x_grad[i, j]))

                grad_mag = np.sqrt(x_grad**2 + y_grad**2)
                grad_dir = np.arctan2(y_grad, x_grad)

                #now we make the magnitude range from 0 to 255
                grad_mag = np.clip(grad_mag / grad_mag.max() * 255, 0, 255).astype(np.uint8)

                strokes1 = [] #format is [pixel_x (j), pixel_y (i)]
                strokes2 = [] #format is [grad_dir of highest error pixel]
                strokes3 = [] #format is [color of highest error pixel]

                for i in range(brush_radius//2, len(np_image)-(brush_radius//2), brush_radius):
                    for j in range(brush_radius//2, len(np_image[0])-(brush_radius//2), brush_radius):

                        patch = np_image3[i-(brush_radius//2):i+(brush_radius//2),j-(brush_radius//2):j+(brush_radius//2)]

                        area_error = 0
                        max_error_pixel = [0, 0]
                        max_error = 0

                        for m in range(len(patch)):
                            for n in range(len(patch)):

                                pixel_error = np.linalg.norm(patch[m, n].astype(np.float32) - np_image[m-(brush_radius//2)+i, n-(brush_radius//2)+j].astype(np.float32))
                                if pixel_error > max_error:
                                    max_error_pixel = [m, n]

                                area_error += pixel_error
                        area_error /= (brush_radius+1)**2

                        if area_error >= error:
                            z = max_error_pixel[0] - (brush_radius//2) + i
                            x = max_error_pixel[1] - (brush_radius//2) + j
                            strokes1.append([x, z])
                            strokes2.append(grad_dir[z, x])
                            strokes3.append(np_image[z, x])

                strokes1 = np.array(strokes1)
                strokes2 = np.array(strokes2)
                step_size = 4 * brush_radius
                x1 = strokes1[:, 0]
                y1 = strokes1[:, 1]
                grad_dirs = strokes2
                
                if random.choice([1, 2]) == 1:
                    normal_dir = grad_dirs + np.pi/2 #randomize + or - pi/2 can be good
                else:
                    normal_dir = grad_dirs + np.pi/2

                dx = step_size * np.cos(normal_dir)
                dy = step_size * np.sin(normal_dir)

                #endpoints
                x2 = x1 + dx
                y2 = y1 + dy

                strokes1_with_endpoints = np.hstack([strokes1, x2[:, np.newaxis], y2[:, np.newaxis]]) #adding to strokes list

                indices = list(range(len(strokes2)))
                random.shuffle(indices) #randomizing stroke order

                #draw strokes
                for i in indices:
                    color = tuple(map(int, strokes3[i])) #convert color to desired format for cv2 line function
                    cv2.line(np_image2, (int(strokes1_with_endpoints[i, 0]), int(strokes1_with_endpoints[i, 1])), (int(strokes1_with_endpoints[i, 2]), int(strokes1_with_endpoints[i, 3])), color, brush_radius)
                    #draw_smooth_line(np_image2, (int(strokes1_with_endpoints[i, 0]), int(strokes1_with_endpoints[i, 1])), (int(strokes1_with_endpoints[i, 2]), int(strokes1_with_endpoints[i, 3])), color, brush_radius)

                np_image3 = np_image2
            
            # for i in range(-3, 4):
            #     a = 260
            #     b = 130
            #     # np_image[b, a + i] = [255, 0, 0]
            #     # np_image[b + 1, a + i] = [255, 0, 0]
            #     # np_image[b + 2, a + i] = [255, 0, 0]
            #     # np_image[b - 1, a + i] = [255, 0, 0]
            #     # np_image[b - 2, a + i] = [255, 0, 0]
            #     # np_image[b - 3, a + i] = [255, 0, 0]
            #     # np_image[b + 3, a + i] = [255, 0, 0]
            # print(grad_dir[b, a])

            # np_imageblur = cv2.bilateralFilter(np_image, (2*16)+1, 75, 75)

            # patch = np_imageblur[b-3:b+4, a-3:a+4]
            # patch = np.mean(patch, axis=2).astype(np.uint8)
            # print(patch)
            # print(np.sum(x_sobel * patch))
            # print(np.sum(y_sobel * patch))
            # print(np.arctan2(np.sum(y_sobel * patch), np.sum(x_sobel * patch)))

            image_2_data = np_im_to_data(np_image2)
            window['-IMAGE2-'].draw_image(data=image_2_data, location=(0, height))



            # #getting back our original image with color
            # np_image2 = np.copy(np_image)

            # testing_edges = 0
            # np_image3 = np.zeros_like(np_image2)
            # # if testing_edges == 1:
            # #     np_image3 = np.copy(np_image2)

            # #sampling pixels to draw lines at just by choosing every third pixel in x and y direction
            # for i in range(1, np_image2.shape[0] - 1):
            #     for j in range(1, np_image2.shape[1] - 1):
            #         stroke_length = random.randint(stroke_length_range[0], stroke_length_range[1])
                    
            #         if testing_edges == 1:
            #             if edges[i, j] == 0:
            #                 np_image3[i, j] = [255, 0, 0]

            #             else:
            #                 np_image3[i, j] = [0, 0, 255]

            #         if testing_edges == 2:
            #             if edges[i, j] == 1:
            #                 np_image3[i, j] = np_image2[i, j]
            #             # else:
            #             #     np_image3[i, j] = [0, 0, 255]

            #         if testing_edges == 0:
            #             #make sure that we aren't on an edge
            #             if edges[i, j] == 0 or edges[i, j] == 1:
            #                 #use the pixel's color for stroke color
            #                 color = (int(np_image2[i, j, 0]), int(np_image2[i, j, 1]), int(np_image2[i, j, 2]))
            #                 # if color == (34, 177, 76):
            #                 #     color = (random.randint(0, 60), random.randint(140, 210), random.randint(40, 110))
            #                 # elif color == (237, 28, 36):
            #                 #     color = (random.randint(200, 255), random.randint(0, 60), random.randint(0, 60))
            #                 # elif color == (0, 162, 232):
            #                 #     color = (random.randint(0, 30), random.randint(130, 190), random.randint(200, 255))

            #                 #using the gradient direction to find the perpindicular direction -y, x
            #                 gradient_angle = grad_dir[i, j]

            #                 #perpindicular x and y directions
            #                 dx = np.sin(gradient_angle)
            #                 dy = -np.cos(gradient_angle)
                            
            #                 #find the endpoints
            #                 end_x = int(j + stroke_length * dx)
            #                 end_y = int(i + stroke_length * dy)
                            
            #                 if edges[i, j] == 0:
            #                     #make sure strokes don't pass through an edge; if they do, shorter them until they don't
            #                     if edges[i:end_y, j:end_x].size > 0 and edges[i:end_y, j:end_x].max() > 0:
            #                         #keep reducing length and checking again if it still passes through an edge
            #                         while edges[i:end_y, j:end_x].max() > 0 and stroke_length > 1:
            #                             stroke_length -= 1
            #                             end_x = int(j + stroke_length * dx)
            #                             end_y = int(i + stroke_length * dy)

            #                             if not edges[i:end_y, j:end_x].size > 0:
            #                                 break

            #                     # if stroke still exists after shortening until it doesn't pass through an edge
            #                     if stroke_length > 1:
            #                         cv2.line(np_image3, (j, i), (end_x, end_y), color, random.randint(stroke_width_range[0], stroke_width_range[1]))
            #                 else:
            #                     cv2.line(np_image3, (j, i), (end_x, end_y), color, random.randint(stroke_width_range[0], stroke_width_range[1]))


            #displaying the altered image
            # image_3_data = np_im_to_data(np_image3)
            # window['-IMAGE2-'].draw_image(data=image_3_data, location=(0, height))
        
        if event == 'Save image':
            save_layout = [
            [sg.Text('Enter filename: (if you do not add an extension, image will be saved as .png)')],
            [sg.Input(key='filename')],
            [sg.Save(), sg.Cancel()]
        ]
            save_window = sg.Window('Save', save_layout)
            save_event, save_values = save_window.read() #this call waits for a button press before continuing so we don't need another event loop
            save_window.close()

            if save_event == 'Save':
                filename = save_values['filename']
                if filename:
                    if not filename.endswith('.png'): #making a default extension in case they don't type one
                        filename += '.png'
                    plt.imsave(filename, np_image2)

        if event == 'Load image':
            load_layout = [
                [sg.Text('Enter the name of the file to be loaded:')],
                [sg.Input(key='filename')],
                [sg.Button('Load'), sg.Cancel()]
            ]
            load_window = sg.Window('Load', load_layout)
            load_event, load_values = load_window.read() #this call waits for a button press before continuing so we don't need another event loop
            load_window.close()

            if load_event == 'Load':
                filename = load_values['filename']
                if filename:
                    np_image = cv2.imread(filename)
                    np_image = cv2.cvtColor(np_image, cv2.COLOR_BGR2RGB)
                    np_image2 = np.copy(np_image)

            #need to find width and height of loaded image before we change GUI canvas size
            new_image_width = len(np_image[0])
            new_image_height = len(np_image)

            #resizing image to be smaller if it is larger than expected
            if new_image_height > 450 or new_image_width > 600:
                if new_image_width > new_image_height:
                    resize_constant = 600/new_image_width
                else:
                    resize_constant = 450/new_image_height

                new_image_width = int(new_image_width*resize_constant)
                new_image_height = int(new_image_height*resize_constant)

                np_image = cv2.resize(np_image, (new_image_width, new_image_height), interpolation=cv2.INTER_LINEAR)
                np_image2 = np.copy(np_image)

            #changing canvas size for loaded image
            window['-IMAGE-'].Widget.config(width=new_image_width, height=new_image_height)
            window['-IMAGE2-'].Widget.config(width=new_image_width, height=new_image_height)

            #putting new images on the canvas
            image_data = np_im_to_data(np_image)
            window['-IMAGE-'].draw_image(data=image_data, location=(0, height))
            image_2_data = np_im_to_data(np_image2)
            window['-IMAGE2-'].draw_image(data=image_2_data, location=(0, height))

            print(np_image2.dtype)

    window.close()

def main():
    parser = argparse.ArgumentParser(description='A simple image viewer.')

    parser.add_argument('file', action='store', help='Image file.')
    args = parser.parse_args()

    print(f'Loading {args.file} ... ', end='')
    image = cv2.imread(args.file)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    print(f'{image.shape}')
    height, width, unused = image.shape

    if height > 450 or width > 600:
        if width > height:
            resize_constant = 600/width
        else:
            resize_constant = 450/height

        width = int(width*resize_constant)
        height = int(height*resize_constant)

        image = cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)

    #now we want to scale down ourwidth to x while maintaining the aspect ratio
    #og_width = image.shape[1]
    #og_height = image.shape[0]

    #width = 200
    #scaling_factor = og_width/width

    #new_height = int(np.round(og_height/scaling_factor))

    #print(f'Resizing the image to 640 width and maintaining aspect ratio ...', end='')
    #image = cv2.resize(image, (width, new_height), interpolation=cv2.INTER_LINEAR)
    #print(f'{image.shape}')

    display_image(image, width, height, args.file)

if __name__ == '__main__':
    main()