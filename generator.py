from PIL import Image, ImageDraw, ImageFont
import sys, struct
from io import BytesIO

character_set = " ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
# split_flap_font = ImageFont.truetype('fonts/DIN Condensed Bold.ttf', 110)
split_flap_font = ImageFont.truetype('fonts/Logisoso.ttf', 160)

xbm_all = open("xbm/split_flap_font.h", "w")
compressed_all = open("split_flap_font_compressed.h", "w") 

count_blocks_total = 0

for char in character_set:
    img = Image.new('1', (64, 128), color = 'black')
    image_draw = ImageDraw.Draw(img)
    character_size = image_draw.textsize(char, font=split_flap_font)
    offset_x = (64-character_size[0])/2

#    image_draw.text((offset_x,25), char, font=split_flap_font, fill='white')
    image_draw.text((offset_x,-15), char, font=split_flap_font, fill='white')
#    image_draw.rectangle([(0,61),(128,65)], fill='black')


    prev_pixel = -1
    count_pixels = 0
    count_blocks = 0
    
    compressed = BytesIO()
    
    px = img.load()
    for i in range(128):
        for j in range (64):
            pixel = px[j,i]
            # if pixel == 0:
            #     sys.stdout.write("0")
            # else:
            #     sys.stdout.write("1")
            if prev_pixel == pixel:
                if count_pixels < 127:
                    count_pixels = count_pixels + 1
                else:
                    print "{} x {}".format(count_pixels, prev_pixel)
                    if prev_pixel == 0:
                        compressed.write(struct.pack("B", count_pixels))
                    else:
                        compressed.write(struct.pack("B", 127+count_pixels))
                    count_pixels = 1
                    count_blocks = count_blocks + 1            
            elif prev_pixel != -1:
                print "{} x {}".format(count_pixels, prev_pixel)
                if prev_pixel == 0:
                    compressed.write(struct.pack("B", count_pixels))
                else:
                    compressed.write(struct.pack("B", 127+count_pixels))
                count_pixels = 1 
                count_blocks = count_blocks + 1            
                
            prev_pixel = pixel

    count_pixels = count_pixels + 1 #final pixel
    if prev_pixel == 0:
        compressed.write(struct.pack("B", count_pixels))
    else:
        compressed.write(struct.pack("B", 127+count_pixels))                
    count_blocks = count_blocks + 1            

    compressed.write(bytearray([0]));
    print count_blocks
    print compressed.tell()
    print("^^^")
    
    compressed_all.write("static const unsigned char char_{}[] PROGMEM = {{".format(char))
    compressed.seek(0)
    uncompressed = []
    while True:
        compressed_byte = struct.unpack("B", compressed.read(1))[0]
        compressed_all.write('0x{:02x}, '.format(compressed_byte))
                
        if compressed_byte == 0:
            break

        pixel = 0
        if compressed_byte > 127:
            pixel = 1
            compressed_byte = compressed_byte - 127
        uncompressed.extend([pixel] * compressed_byte)    

    print(len(uncompressed))

    for i in range(128):
        for j in range (64):
            pixel = uncompressed[i * 64 + j]
            if pixel == 0:
                sys.stdout.write("0")
            else:
                sys.stdout.write("1")
        print("")
    
    print("---")

    count_blocks_total += count_blocks

    img.save('out/{}.bmp'.format(char))

    xbm_file_name = 'xbm/{}.xbm'.format(char)
    img.save(xbm_file_name)
    f = open(xbm_file_name, mode='r')
    xbm_temp = f.read()
    f.close()

    xbm_temp = xbm_temp.replace("static char im_bits[]", "static const unsigned char char_{}[] PROGMEM".format(character_set.index(char)));
    xbm_all.write(xbm_temp) 
    
    compressed_all.write("};\n")  

print count_blocks_total

xbm_all.write('static const char char_set[] = "' + character_set + '";\n')

xbm_all.write('static const unsigned char* char_map[] = {')
xbm_all.write(",".join(["char_{}".format(character_set.index(char)) for char in character_set]))
xbm_all.write('};')

compressed_all.write('static const char char_set[] = "' + character_set + '";\n')

compressed_all.write('static const unsigned char* char_map[] = {')
compressed_all.write(",".join(["char_{}".format(character_set.index(char)) for char in character_set]))
compressed_all.write('};')

xbm_all.close()
compressed_all.close()
