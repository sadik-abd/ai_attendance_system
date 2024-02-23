import requests
from datetime import datetime
# URL of the endpoint

# Send GET request
def img_save(url, label):
    response = requests.get(url, stream=True)

    # Check if the request was successful
    if response.status_code == 200:
        jpg_content = bytearray()
        in_jpeg = False
        for chunk in response.iter_content(chunk_size=1024):
            # Iterate through each byte
            for byte in chunk:
                if byte == 0xff:  # Possible start of JPEG marker
                    jpg_content.append(byte)  # Add it to array
                    in_jpeg = True
                elif in_jpeg:
                    jpg_content.append(byte)
                    if jpg_content[-2:] == bytes([0xff, 0xd9]):  # JPEG end marker
                        # Save the image
                        with open(label+"_"+datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'wb') as f:
                            f.write(jpg_content)
                        print("Image saved as image.jpg")
                        in_jpeg = False  # Reset for the next image
                        break  # Exit after saving the first image
            if not in_jpeg:  # Break the outer loop if we've finished processing a JPEG
                break
    else:
        print("Failed to retrieve the image")

if __name__ == "__main__":
    url = 'http://127.0.0.1:3232/video_feed'
    img_save(url)