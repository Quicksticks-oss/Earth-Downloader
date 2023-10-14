from PIL import Image
from itertools import product
import requests
import time
import os

logo = '''                      ░░▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒░░                      
                  ▒▒▓▓▓▓▓▓▓▓▒▒▒▒░░▒▒▓▓▓▓▓▓▓▓▓▓▒▒                  
              ░░▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░▒▒▓▓▓▓▓▓▓▓▓▓▓▓▒▒              
            ▓▓▒▒▒▒▓▓▓▓▓▓▓▓▒▒▓▓▓▓▒▒░░▓▓▓▓▓▓▓▓▓▓▒▒▓▓▓▓▓▓            
          ██▓▓▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▒▒▓▓▓▓▓▓          
        ██▓▓▒▒▒▒▒▒▓▓▓▓▓▓▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▓▓▒▒▓▓▓▓        
      ▓▓▓▓▒▒▒▒▒▒▒▒▒▒▓▓▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓▓▓▓▓▓▓▓▒▒▒▒▒▒      
    ▒▒██▒▒░░░░▒▒▒▒▓▓▓▓▓▓▒▒▓▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓▓▒▒▓▓▓▓▓▓▓▓░░    
    ████▒▒▒▒░░▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████▓▓▓▓▓▓▓▓████▒▒▒▒▓▓▒▒▓▓▓▓    
  ▓▓██▓▓▒▒░░▒▒▒▒▓▓▓▓▒▒▒▒▓▓▓▓████████████▓▓▓▓▓▓██▓▓▓▓▓▓▒▒▓▓▒▒▓▓▒▒  
  ██▓▓▓▓░░░░▓▓▓▓▓▓▒▒▓▓▓▓▓▓████████████▓▓▓▓▓▓████▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒  
  ██▓▓▓▓░░▒▒▓▓▒▒▓▓▓▓▓▓██████████████▓▓▓▓▓▓▓▓████▓▓▓▓▒▒▒▒▓▓░░▒▒▒▒░░
▓▓██▓▓▓▓░░▓▓▓▓▓▓▓▓▓▓▓▓██████████████▓▓▓▓████████▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒
██▓▓▓▓▓▓░░▓▓▓▓▓▓▓▓▒▒▓▓██████████████▓▓██████████▓▓▓▓▒▒▓▓▓▓▒▒▒▒▓▓▒▒
████▓▓▓▓▓▓▓▓▒▒▓▓██▓▓▓▓▓▓████████████▓▓██████████▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒
██▓▓▓▓▓▓▓▓▓▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓████████▓▓████████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒
██▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▓▓▓▓▓▓██▓▓▓▓██████▓▓████████████▓▓▓▓▒▒▒▒▓▓▓▓▒▒▒▒                
'''

def download_sat(zoom=3, pos_x=1, pos_y=2):
    server = f'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{pos_y}/{pos_x}'
    downloaded = False
    while not downloaded:
        try:
            r = requests.get(server)
            downloaded = True
        except Exception as ex:
            print('Time OUT!', ex)
            time.sleep(120)

    directory_path = f"{zoom}"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    
    save_file = f'{directory_path}/{zoom}_{pos_y}_{pos_x}.jpg'
    with open(save_file, 'wb+') as f:
        f.write(r._content)
    return save_file

def split_image(image, chunk_width, chunk_height):
    width, height = image.size
    for x in range(0, width, chunk_width):
        for y in range(0, height, chunk_height):
            chunk = image.crop((x, y, x + chunk_width, y + chunk_height))
            yield chunk

def quick_save(images):
    widths, heights = zip(*(i.size for _, i in images))
    total_width = max(widths)*maps_x
    max_height = max(heights)*maps_y
    new_im = Image.new('RGB', (total_width, max_height))
    print(f"Creating new image: {total_width}x{max_height}")
    last_y = 0
    x_offset = 0
    for (y_, im) in images:
        if last_y != y_:
            x_offset = 0
        new_im.paste(im, (x_offset, y_*im.size[0]))
        x_offset += im.size[1]
        last_y = y_
    print('Saving image...')

    chunk_size = (8192, 8192)

    if (total_width + max_height) < (chunk_size[0]+chunk_size[1]):
        new_im.save(f'chunks/chunk_1.png')
        return

    directory_path = f"chunks"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Split the image into 4k-sized chunks and save them
    chunk_index = 1
    for chunk in split_image(new_im, chunk_size[0], chunk_size[1]):
        chunk.save(f'chunks/chunk_{chunk_index}.png')
        chunk_index += 1

    print(f'Saved {chunk_index - 1} chunks.')

def convert_seconds(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return hours, minutes, seconds

if __name__ == '__main__':
    print(logo, '\n')
    input('Press enter to start download...')
    #7, 15, 31
    images = []
    zoom = int(input('Zoom scale > '))
    print('Started download of world map...')
    maps_y = 2**zoom
    maps_x = maps_y
    print(f'Map Size: {zoom-2}, {maps_x*256}x{maps_y*256}')
    start_time = time.time()
    total = maps_y*maps_x

    for y in range(maps_y):
        for x in range(maps_x):
            s = download_sat(zoom=zoom, pos_x=x, pos_y=y)
            images.append((y, Image.open(s)))
            current_iteration = y * maps_x + x + 1
            remaining_iterations = total - current_iteration
            current_time = time.time() - start_time
            estimated_time_remaining = (current_time / current_iteration) * remaining_iterations
            hours, minutes, seconds = convert_seconds(estimated_time_remaining)
            print(f'Iteration {current_iteration}/{total}, Remaining: {remaining_iterations}, Currently Download Cords: X({x})/X({maps_x}) and Y({y})/Y({maps_y}), {hours:.0f}:{minutes:.0f}:{seconds:.0f} hr/m/s left until fully downloaded...', end='\r')
        quick_save(images)

    quick_save(images)
    print('Downloaded World!')