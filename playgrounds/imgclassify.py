from appJar import gui
import os, pickle, sys, glob

count = 0
data = {}

fn = lambda: f"out_scans/{count}.png"
total = len(glob.glob("out_scans/*.png"))

def img():
    fn_ = fn()
    if os.path.exists(fn_):
        return fn_
    elif count > total:
        done()
    else:
        data[count] = None
        img()

def update():
    global app
    app.setImage("Img", img())
    app.setLabel("iter", f"{count}/{total}")

def add(state):
    global count
    data[count] = state
    count += 1
    update()

y = lambda: add(True)
n = lambda: add(False)

def done():
    global data
    f = open("state.bin", 'wb')
    pickle.dump(data, f)
    f.close()
    print("Done, closing")
    sys.exit(0)

def back():
    global count
    count -= 1
    update()

app = gui("plz end me ty")
app.addImage("Img", fn())
app.addLabel("iter", f"{count}/{total}")
app.addButton("Yes", y)
app.addButton("No", n)
app.addButton("Back", back)
app.addButton("Done", done)
app.bindKey("y", y)
app.bindKey("n", n)
app.bindKey("d", done)
app.bindKey("b", back)

app.go()