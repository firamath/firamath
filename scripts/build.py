import fontforge

src_path = "./src/"
otf_path = "./docs/assets/"
family_name = "FiraMath"
family_name_full = "fira-math"
weights = ["thin", "light", "regular", "medium", "bold"]
sfd_suffix = ".sfdir"
otf_suffix = ".otf"

print("FontForge version: " + fontforge.version())

for i in weights:
    file_name = src_path + family_name_full + "-" + i + sfd_suffix
    font = fontforge.open(file_name)
    font.generate(otf_path + family_name + "-" + i.capitalize() + otf_suffix, flags=("opentype"))
print("Generating finished!")
