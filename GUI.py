import io
import DataToImage as DTI
import PySimpleGUI as sg
from PIL import Image


def save_or_load_image(save_as=False, title='Choose Image'):
    return sg.popup_get_file(title, file_types=(('PNG', '*.png'),), no_window=True, save_as=save_as)

def image_to_bios(image, size: tuple):
    """
    Saves a PIL image to bios after it gets resized and keeps it's ratio
    and returns it's value as a base64 encoded data.
    :param image: A PIL image to get as a base64 encoded data
    :type image: PIL.Image
    :param size: The wanted size of the image
    :type size: Tuple(int, int)
    :return: The image as a base64 encoded data
    :rtype: str
    """

    image.thumbnail(size)
    bio = io.BytesIO()
    image.save(bio, format="PNG")
    value = bio.getvalue()
    bio.close()
    return value


start_column = [
    [sg.Button('Encode Data')],
    [sg.Button('Decode Data')]
]

decode_column = [
    [sg.Button('Choose Image to decode', key='-LOAD_IMAGE_TO_DECODE-')],
]

encode_column = [
    [sg.Button('Choose Image', key='-LOAD_IMAGE-'), sg.Image(size=(100, 100), key='-IMAGE-')],
    [sg.Column([[sg.Text('Data to encode:', visible=True), sg.Input('Hello bro (it\'s a secret message 😋)', key='-MSG_IN-', visible=True, enable_events=True)]], key='-MSG_COL-', visible=False)],
    [sg.Button('Merge Text Into The Image', key='-MERGE-', visible=False, tooltip='Ready to merge!')]
]

layout = [
    [
        sg.Column(start_column, key='-COL1-', visible=True),
        sg.Column(decode_column, key='-COL2-', visible=False),
        sg.Column(encode_column, key='-COL3-', visible=False)
     ]
]

window = sg.Window('Image Messenger', layout)
image_loaded = False

while True:
    event, values = window.read()

    # ---- Switch windows ---- #
    if event == 'Encode Data':
        window['-COL1-'].update(visible=False)
        window['-COL3-'].update(visible=True)

    if event == 'Decode Data':
        window['-COL1-'].update(visible=False)
        window['-COL2-'].update(visible=True)

    # ---- Encode ---- #
    if event == '-LOAD_IMAGE-':
        file = save_or_load_image()

        try:
            file_data = image_to_bios(Image.open(file, 'r'), size= (200, 200))
        except:
            sg.popup_error('Invalid Image!')
            image_loaded = False
            continue

        window['-IMAGE-'].update(data=file_data)
        image_loaded = True

    if image_loaded:
        window['-MSG_COL-'].update(visible=True)
        window['-MERGE-'].update(visible=True)
    else:
        window['-MSG_COL-'].update(visible=False)
        window['-MERGE-'].update(visible=False)

    data_text = values['-MSG_IN-']

    if data_text == '':
        window['-MERGE-'].update(disabled=True)
        window['-MERGE-'].set_tooltip("The 'Data to encode' can't be empty!")
    else:
        window['-MERGE-'].update(disabled=False)
        window['-MERGE-'].set_tooltip("Ready to merge!")

    if event == '-MERGE-':
        img = DTI.encode(data_text, file)
        save = save_or_load_image(True, 'Save encoded message')
        img.save(save, 'PNG')

    # ---- Decode ---- #
    if event == '-LOAD_IMAGE_TO_DECODE-':
        img_path = save_or_load_image()
        sg.easy_print(DTI.decode(img_path))

    if event == sg.WINDOW_CLOSED:
        break

window.close()