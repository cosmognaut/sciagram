#set text(
  font: "New Computer Modern",
  size: 14pt
)
#set page(
  paper: "a4",
  margin: (x: 1.6cm, y:1.5cm)
)

#set par(
  justify: true,
  leading: 0.52em,
)

#set document(
  author: "cosmog",
  title: [Some notes for `sciagram`]
)

#set heading(numbering: "1.a.") // try 1. 1.a. and whatnot

#align(center, [
    #title()
  ]
)
`sciagram` is a toy project concerned with rendering ASCII art from image files for now. The exact approaches for calculating brightness/color, etc. are detailed in `src/`. Here, we are only concerned with constraints to the project, and possible approaches around that. 

= The problem of scaling
It turns out that fonts rendered on the terminal (via a terminal emulator) are not square-shaped. This is expected, as letters too are usuall rectangular in nature. Consider the letter *I*. It's taller than it's wide. Or consider *T* or *E* or even *P*. All of these letters have a greater height than width. Thus, font families too render text on the screen, and each _cell_ that they fill with text has greater height than width.

#figure(
  image("./assets/cursor.png", width:30%, height:30%),
  caption: [
   Screenshot of a blinking cursor in my current terminal configuration. See how the height is much greater than the width.
  ],
) <cursor> // this is a label I will use to refer to that image.

This is an important distinction, as in this project I am concerned with rendering ASCII art to the terminal. We can easily get the length and width of the attached terminal using `shutil.get_terminal_size`. This approach is taken because it allows for a _fallback_ value, defaulting to `(80, 24)`. Before we render the ASCII art to the terminal, we should resize it, so that it's visible on the current terminal screen in its entirety. The naive approach taken by myself here was to do
```python
image = image.resize((term_cols, term_rows))
```
Here `term_rows` and `term_cols` are the number of lines in the terminal (its height) and the number of columns (its width). Note that both of these values are denoted in terms of _cells_.

I call this approach naive because it doesn't take into account the proportions of an image. Let's say that an image of size `420x540` is presented to the converter. We resize it to `173x35` based on the current terminal size. But by doing this we have absolutely trashed the aspect ratio of the original image; the original had more length than width (`540` vs `420`), while in the latter it's the opposite. Worse yet, from @cursor it's evident that the cell width and height are to be taken into account too, as `173 x cell_width` and `35 x cell_height` is really what we are seeing here for each pixel/ASCII character. So even if we got the aspect ratio right from a terminal point of view, we will still render the final in a squished up or stretched version of itself, purely because of how cells are rendered in the terminal.

Thus, in this part we are concerned with finding a formula that _scales_ the resulting art's width and height according to some factor, so that the image's original proportions are preserved.

== Derivation: a formula to calculate the amount of scaling
Let's set the stage first. Consider:

$
c_w = "cell width"\
c_h = "cell height"\
T_c = "number of columns in the terminal"\
T_r = "number of lines or rows in the terminal"\
t_c = "target columns, or the final number of columns in the rendered art"\
t_r = "target rows, or the final number of lines or rows in the rendered art"\
$

Our goal here is to determine $t_c$ and $t_r$, as all the other values are fixed. How? $T_c$ and $T_r$ can be determined `shutil.get_terminal_size` to determine the dimensions of the final canvas. $c_w$ and $c_h$ are fixed values for a particular font family and font size. Thus, our approach will be trying to determine how to express $t_c$ and $t_r$ in terms of everything else.

Let's concern ourselves with the cell's own dimensions. These are genuinely unknown. We can't know `c_w` and `c_h`, but we can know the ratio between them:
$
alpha = c_w/c_h = "cell ratio or font-correction ratio"
$
For most monospace fonts, $alpha = 1/2 = 0.5$, which means that the height is twice the width. For my particular font, $alpha = 1/2.5 = 0.4$.

Now the physical width of our final render would be
$
p_w = t_c times c_w
$
And the physical height of the render would be
$
p_h = t_r  times c_h
$
Taking the ratio here, we get
$
p_w/p_h = (t_c times c_w)/(t_r times c_h) = alpha times (t_c/t_r) => (1)
$
For the image's original proportion, we can use the _aspect ratio_, which is defined as the ratio of width of the image to its height.
$
"aspect ratio" = w_im/h_im => (2)
$

Here, we want to preserve the image's proportions during the render, so we want the final render's proportions to be equal to the image's aspect ratio. Using (1) and (2):
$
p_w/p_h = w_im/h_im\
=> p_w/p_h = alpha times (t_c/t_r) = w_im/h_im => (3)
$

Now, let's consider that the final render's total number of columns is a function of the width of the original image, $w_im$. The reasoning behind this is that we are _scaling_ the width of the image by some factor, say $s$, which makes the width either stretch out or squish up in accordance to the present constraints (i.e. terminal size and number of cells). That is,
$
t_c = w_im times s => (4)
$
where $s$ is some arbitrary "scaling factor".

Think about this - if $s$ is 1.0, it means that the original image's width and the final render's width are the same. If the value of $s$ is 0.5 instead, the final render's width is half of the image's width. This means that $s$ here represents the amount of *zoom* we are applying to the image. In regular photos too, you would observe that the amount of zoom always preserves the aspect ratio of the image, which is exactly our intention here. Think of it as us trying to zoom the image in or out based on the dimensions of the terminal.

Using (3) and (4), we can also derive the value of $t_r$ in terms of $s$
$
t_r = h_im times s times alpha => (5)
$
Now, let's apply the actual constraints here:
$
t_c <= T_c => (6)\
t_r <= T_r => (7)
$
That is, the final art's width can be at max. the width of the terminal itself, and the final art's height can be at max. the height of the terminal itself.

Using (4) and (5) along with (6) and (7), we can get
$
s <= T_r/(h_im times alpha); s <= T_c/w_im
$
The value that $s$ takes would be the minimum of the two, as we have two $<=$ signs here. Thus,
$
s = min(T_r/(h_im times alpha), T_c/w_im)
$
Therefore, this value is dependent on the width and height of the original image, as well as the terminal's own size (in cells), and the cell ratio. Finally, we can use (4) and (5) to calculate the final art's total lines and total columns. This tuple $(t_c, t_r)$ is exactly what we would use to resize the image to preserve its original proportions.

=== But what if I scale the total lines (rows) instead?
You can absolutely do that, in that case (4) becomes:
$
t_r = h_im times s
$
And for the number of columns you would get
$
t_c = (w_im times s)/alpha
$
It doesn't matter if you scale the lines or the columns; $s$ merely represents some number you multiply the width or the height by some factor, which is what the final render's dimensions would look like. Thus, you can freely scale across either the horizontal or the vertical directions.

=== What if I want to display the final image in maximum resolution?
The current discussion is only considered with *fitting* the image to the terminal size. If you want to display the image in maximum resolution, you would need to first figure out whether the attached terminal has more width than height (the height can be more in certain setups). Then, you max out whatever value was greater (width or height) to the max size of the terminal ($T_c$ or $T_r$). Which means
$
t_c = T_c "(if terminal width is to be maximised)"\
t_r = T_r "(if terminal height is to be maximised)"
$
In most cases, you would need the former. For the second value, you would just use the previous formulas (either (4) or (5)) and calculate that. It's simple.
