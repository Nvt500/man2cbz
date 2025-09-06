import os
import io
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import click
import PIL.Image
import PIL.ImageTk
import cbz
import cbz.page

from src import constants


@click.command()
@click.help_option("-h", "--help")
def ui() -> None:
    """Open a ui to read cbz files locally"""

    root = tk.Tk()

    images = []

    # Left side chapter list
    chapter_frame = tk.Frame(root)
    chapter_frame.pack(side="left", fill="y")

    def open_file() -> None:
        filename = tk.filedialog.askopenfilename(
            title="Open a file",
            initialdir=constants.get_root_dir(),
            filetypes=(("cbz files", "*.cbz"),),
        )
        if not filename:
            return
        chaps = get_images(filename)
        if chaps is None:
            tk.messagebox.showwarning(title="Open Failed", message=f"{filename} is empty or failed to open.")
            return
        images.clear()
        for chap in chaps:
            images.append(chap)
        init(images, canvas, listbox)

    open_file_button = tk.Button(chapter_frame, text="Open File", anchor="n", command=open_file)
    open_file_button.pack(side="top", fill="x")
    previous_button = tk.Button(chapter_frame, text="Previous Chapter", anchor="n")
    previous_button.pack(side="top", fill="x")
    next_button = tk.Button(chapter_frame, text="Next Chapter", anchor="n")
    next_button.pack(side="top", fill="x")

    listbox_scroll = tk.Scrollbar(chapter_frame, orient="vertical")
    listbox_scroll.pack(side="right", fill="y")

    listbox = tk.Listbox(chapter_frame)
    listbox.config(yscrollcommand=listbox_scroll.set)
    listbox.pack(side="left", fill="y")

    listbox_scroll.config(command=listbox.yview)

    # Right side image view
    image_frame = tk.Frame(root)
    image_frame.pack(side="top", fill="both", expand=True)

    image_scroll = tk.Scrollbar(image_frame, orient="vertical")
    image_scroll.pack(side="right", fill="y")

    canvas = tk.Canvas(image_frame)
    canvas.config(scrollregion=canvas.bbox("all"), yscrollcommand=image_scroll.set)
    canvas.pack(side="top", fill="both", expand=True)

    image_scroll.config(command=canvas.yview)

    canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * e.delta / (120 if os.name == "nt" else 1)), "units"))
    listbox.bind("<<ListboxSelect>>", lambda e: add_images(canvas, images[listbox.curselection()[0]]))
    previous_button.bind("<Button-1>", lambda e : change_chapter(-1, canvas, images, listbox))
    next_button.bind("<Button-1>", lambda e : change_chapter(1, canvas, images, listbox))

    root.geometry("1000x800")
    tk.mainloop()


def init(images: list[list[PIL.ImageTk.PhotoImage] | list[cbz.page.PageInfo]], canvas: tk.Canvas, listbox: tk.Listbox) -> None:
    """Initialize canvas and listbox with images"""

    listbox.delete(0, tk.END)
    for i in range(len(images)):
        listbox.insert(tk.END, f"Chapter {i + 1}")
    listbox.selection_set(0)

    add_images(canvas, images[0])


def change_chapter(change: int, canvas: tk.Canvas, images: list[list[PIL.ImageTk.PhotoImage] | list[cbz.page.PageInfo]], listbox: tk.Listbox) -> None:
    """Changes the chapter by the value change"""

    if not images:
        return
    if listbox.curselection()[0] + change < 0 or listbox.curselection()[0] + change >= len(images):
        return
    changed = listbox.curselection()[0] + change
    add_images(canvas, images[changed])
    listbox.selection_clear(0, tk.END)
    listbox.selection_set(changed, changed)


def add_images(canvas: tk.Canvas, images: list[PIL.ImageTk.PhotoImage] | list[cbz.page.PageInfo]) -> None:
    """Adds images to the canvas"""

    canvas.yview_moveto(0)
    canvas.delete("all")
    next_height = 0
    for i, image in enumerate(images):
        if isinstance(image, cbz.page.PageInfo):
            image = PIL.ImageTk.PhotoImage(PIL.Image.open(io.BytesIO(image.content)))
            images[i] = image
        canvas.create_image(0, next_height, image=image, anchor="n")
        next_height += image.height()
    canvas.config(scrollregion=canvas.bbox("all"))
    canvas.pack(side="top", fill="both", expand=True)


def get_images(cbz_path: str) -> list[list[cbz.page.PageInfo]] | None:
    """Gets a list of each chapter's images from the cbz file"""

    images = [[]]
    try:
        comic = cbz.ComicInfo.from_cbz(cbz_path)
    except AttributeError:
        return None
    for page in comic.pages:
        chapter = int(page.key.lstrip("Chapter").split("Image")[0])
        try:
            images[chapter - 1].append(page)
        except IndexError:
            images.append([])
            images[chapter - 1].append(page)
    return images
