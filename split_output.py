with open("/tmp/build.log") as f:
    data = f.read()
html = data.split("---HTML---")[1]

with open("website/index.html", "w") as out:
    parts = html.split("\n")
    for part in parts:
        if part.strip():
            out.write(part[10:])
            out.write("\n")