from PIL import Image
# https://docs.python.org/3/howto/urllib2.html
import urllib.request
import io
import os


def get_flag(url, dest_file):
    request = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36"})
    with urllib.request.urlopen(request) as response:
        the_page = response.read()
        f = io.open(dest_file, "bw")
        f.write(the_page)
        f.close()


def compile_flags(country_list, filename):
    compiled_flags = Image.new("RGB", (60, 40))

    left = 2
    top = 12
    right = 64 - 2
    bottom = 64 - 12

    x = 0

    limit = 6

    for i in range(0, len(country_list)):

        if i > limit:
            break

        if country_list[i].lower() == "ch":
            img = Image.open("./switzerland.png")
            img_new = img.crop((12, top, (64-12), bottom))
            compiled_flags.paste(img_new, (x, 0))
            # print("Switzerland is in the list.")

        else:
            get_flag(f"https://www.countryflags.io/{country_list[i].lower()}/flat/64.png", f"{filename}flag{i}.png")

            img = Image.open(f"./{filename}flag{i}.png")
            img_new = img.crop((left, top, right, bottom))
            compiled_flags.paste(img_new, (x, 0))
            os.remove(f"./{filename}flag{i}.png")

        if len(country_list) <= limit:
            x += round(60 / len(country_list))
        else:
            x += round(60 / limit)

    compiled_flags.save(f"{filename}compiled_flags.png")
    # compiled_flags.show()
    # print(len(country_list))


# compile_flags(["gr", "gb", "CH"])
# compile_flags(["gr", "gb", "nl", "de", "fr", "cn", "ca", "us", "au", "se", "qa", "fj", "lu", "nf", "it"])
