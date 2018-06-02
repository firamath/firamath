import fontforge
from datetime import datetime

sfd_path = "./src/"
otf_path = "./docs/assets/"
family_name = "FiraMath"
family_name_full = "fira-math"
weights = ["thin", "light", "regular", "medium", "bold"]
sfd_suffix = ".sfdir"
otf_suffix = ".otf"

print("FontForge version: " + fontforge.version() + "\n")

for i in weights:
    sfd_name = sfd_path + family_name_full + "-" + i + sfd_suffix
    font_name = family_name + "-" + i.capitalize()
    font = fontforge.open(sfd_name)
    font.generate(otf_path + font_name + otf_suffix, flags=("opentype"))
    print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S.%f]')
        + " '" + font_name + "' " + "generated successfully.")
