import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from build_kit import mermaid, notebook, slides, pdf_from_markdown, workbook

sys.path.insert(0, str(HERE))
import figures
from nb_cells import all_notebooks

IMG = HERE / "images"


def mermaid_diagrams():
    mermaid("""
flowchart LR
    V[Vectors] --> E[Embeddings<br/>Mod 06, 09]
    D[Dot product and<br/>cosine similarity] --> S[Semantic search<br/>and RAG]
    M[Matrices] --> L[Neural-network layers<br/>Mod 05]
    P[Probability and<br/>softmax] --> T[LLM next-token choice<br/>temperature, Mod 07]
    G[Derivatives and<br/>gradient descent] --> R[Training every model<br/>Mod 04, 05, 13]
    F[Loss functions] --> R
""", IMG / "math_map.png")
    mermaid("""
flowchart LR
    A[Weights<br/>start random] --> B[Predict<br/>X @ W + b]
    B --> C[Loss<br/>how wrong?]
    C --> D[Gradient<br/>slope for each weight]
    D --> E[Update<br/>w = w - lr x slope]
    E -->|repeat| B
    C -->|loss small enough| F[Trained model]
""", IMG / "training_loop.png")


def excel():
    readme = [
        ["Sheet", "What it shows", "Try this"],
        ["Dot & cosine", "Dot product, vector lengths and cosine similarity with live formulas", "Change the numbers in columns B and C"],
        ["Softmax", "Scores (logits) -> probabilities, with a temperature cell and cross-entropy", "Set temperature to 0.5, then 2"],
        ["Gradient descent", "20 steps of gradient descent on loss = (w - 3)^2 + 1", "Set learning rate to 0.9, then 1.1 (diverges)"],
        ["GD fit a line", "Gradient descent learns w and b of y = w*x + b from 5 points", "Change the y values or the learning rate"],
        ["Matrix multiply", "A (2x3) @ B (3x2) = C (2x2), each cell a row-times-column formula", "Change any number in A or B"],
        ["Mean & variance", "Mean, deviations, variance and standard deviation step by step", "Add an extreme value and watch the spread"],
        ["Note", "Type over any plain number to change it; cells holding formulas recalculate automatically in Excel, LibreOffice or Google Sheets.", ""],
    ]
    dot = [
        ["Item", "a", "b", "a x b", "Notes"],
        ["component 1", 2, 4, "=B2*C2", "multiply matching pairs..."],
        ["component 2", 1, 0, "=B3*C3", ""],
        ["component 3", 3, 1, "=B4*C4", ""],
        ["component 4", 0, 2, "=B5*C5", ""],
        ["dot product a . b", None, None, "=SUM(D2:D5)", "...then add them up"],
        ["same with SUMPRODUCT", None, None, "=SUMPRODUCT(B2:B5,C2:C5)", "Excel's built-in dot product"],
        ["length (norm)", "=SQRT(SUMSQ(B2:B5))", "=SQRT(SUMSQ(C2:C5))", None, "square, add, square root"],
        ["cosine similarity", None, None, "=D6/(B8*C8)", "dot / (length a * length b): between -1 and 1"],
        ["Shopping bill example", "quantity", "price", "qty x price", ""],
        ["mouse", 2, 799, "=B11*C11", ""],
        ["headphones", 1, 2499, "=B12*C12", ""],
        ["notebook", 3, 249, "=B13*C13", ""],
        ["total bill = dot product", None, None, "=SUMPRODUCT(B11:B13,C11:C13)", "a receipt is a dot product"],
    ]
    words = [("cat", 3.0), ("dog", 2.2), ("car", 1.0), ("tree", 0.4), ("sky", -0.5)]
    soft = [["Word", "score (logit)", "score / T", "exp(score / T)", "probability", "Notes"],
            ["temperature T", 1, None, None, None, "change me: 0.5 = sharp, 2 = flat"]]
    for i, (w, s) in enumerate(words, start=3):
        soft.append([w, s, f"=B{i}/$B$2", f"=EXP(C{i})", f"=D{i}/SUM($D$3:$D$7)", ""])
    soft.append(["total", None, None, "=SUM(D3:D7)", "=SUM(E3:E7)", "probabilities always add up to 1"])
    soft.append(["cross-entropy if 'cat' is correct", None, None, None, "=-LN(E3)", "-log(probability of the correct word)"])
    soft.append(["cross-entropy if 'sky' is correct", None, None, None, "=-LN(E7)", "low probability -> big loss"])

    gd = [["Setting", "Value", "", "", "", "Notes"],
          ["learning rate", 0.1, None, None, None, "try 0.9 (bounces but settles) and 1.1 (blows up)"],
          ["start w", -1, None, None, None, "where we start"],
          ["loss function", "(w - 3)^2 + 1", None, None, None, "slope = 2*(w - 3); the minimum is at w = 3"],
          [],
          ["step", "w", "loss", "slope", "new w = w - lr * slope", ""]]
    for k in range(21):
        r = 7 + k
        w = "=B3" if k == 0 else f"=E{r - 1}"
        gd.append([k, w, f"=(B{r}-3)^2+1", f"=2*(B{r}-3)", f"=B{r}-$B$2*D{r}", ""])

    fit = [["x", "y", "", "Setting", "Value", "Notes"],
           [1, 3, None, "learning rate", 0.05, "true line is y = 2x + 1. w gets close fast; b creeps towards 1 slowly. Copy the last row down for more steps."],
           [2, 5, None, "n (points)", "=COUNT(A2:A6)", ""],
           [3, 7, None, None, None, ""],
           [4, 9, None, None, None, ""],
           [5, 11, None, None, None, ""],
           [],
           ["step", "w", "b", "MSE", "dMSE/dw", "dMSE/db"]]
    for k in range(41):
        r = 9 + k
        w = 0 if k == 0 else f"=B{r - 1}-$E$2*E{r - 1}"
        b = 0 if k == 0 else f"=C{r - 1}-$E$2*F{r - 1}"
        err = f"(B{r}*$A$2:$A$6+C{r}-$B$2:$B$6)"
        fit.append([k, w, b, f"=SUMPRODUCT({err}^2)/$E$3", f"=2*SUMPRODUCT({err}*$A$2:$A$6)/$E$3",
                    f"=2*SUMPRODUCT({err})/$E$3"])

    mm = [["", "A (2x3)", "", "", "", "B (3x2)", "", "", "C = A @ B (2x2)", ""],
          ["", "col 1", "col 2", "col 3", "", "col 1", "col 2", "", "col 1", "col 2"],
          ["row 1", 1, 2, 3, "", 7, 8, "", "=B3*F3+C3*F4+D3*F5", "=B3*G3+C3*G4+D3*G5"],
          ["row 2", 4, 5, 6, "", 9, 10, "", "=B4*F3+C4*F4+D4*F5", "=B4*G3+C4*G4+D4*G5"],
          ["row 3", None, None, None, "", 11, 12, "", None, None],
          [],
          ["How to read it", "C row i, col j = row i of A dotted with column j of B. (2x3) @ (3x2): inner 3 = 3, result 2x2."]]

    data = [12, 15, 11, 14, 18, 10, 13, 15]
    mv = [["value", "deviation (value - mean)", "squared deviation", "", "Result", "Value", "Notes"]]
    n = len(data)
    for i, v in enumerate(data, start=2):
        mv.append([v, f"=A{i}-$F$2", f"=B{i}^2", None, None, None, None])
    last = n + 1
    mv[1][4:7] = ["mean", f"=AVERAGE(A2:A{last})", "the centre"]
    mv[2][4:7] = ["variance", f"=AVERAGE(C2:C{last})", "average squared distance from the mean"]
    mv[3][4:7] = ["standard deviation", "=SQRT(F3)", "same units as the data"]
    mv[4][4:7] = ["check: sum of deviations", f"=SUM(B2:B{last})", "always 0"]

    workbook({"Read me": readme, "Dot & cosine": dot, "Softmax": soft, "Gradient descent": gd,
              "GD fit a line": fit, "Matrix multiply": mm, "Mean & variance": mv},
             HERE / "excel" / "math-in-a-spreadsheet.xlsx",
             col_widths={"Read me": [18, 70, 45], "Dot & cosine": [26, 20, 20, 30, 42],
                         "Softmax": [32, 14, 12, 16, 14, 40], "Gradient descent": [14, 14, 12, 12, 22, 48],
                         "GD fit a line": [8, 12, 12, 14, 14, 60], "Matrix multiply": [14, 10, 10, 10, 4, 10, 10, 4, 22, 22],
                         "Mean & variance": [10, 24, 18, 4, 24, 12, 38]})


def deck():
    I = lambda n: str(IMG / n)
    return {
        "title": "Module 03 - Math for AI",
        "subtitle": "Intuition only: vectors, matrices, probability, gradients",
        "slides": [
            {"title": "Everything becomes a list of numbers",
             "bullets": ["Photos -> grids of pixel numbers", "Sentences -> embeddings (lists of numbers)", "Models -> millions of weights (numbers)",
                         "Today: tools to compare, combine and adjust those lists", "No proofs, only pictures and NumPy"],
             "notes": "Reassure the room: nobody needs to be a mathematician. The one big idea is that in AI everything turns into lists of numbers. Today's maths is just the toolkit for comparing, combining and adjusting those lists. We will compute everything in NumPy and see it in a spreadsheet."},
            {"title": "Where each idea shows up", "image": I("math_map.png"),
             "bullets": ["Vectors -> embeddings", "Cosine -> search and RAG", "Matrices -> layers", "Softmax -> next token", "Gradients -> training"],
             "notes": "This map links each topic to a later module. When students ask why they need this, point here. Cosine similarity powers RAG in module 9, softmax and temperature appear in module 7, gradient descent trains every model in modules 4, 5 and 13."},
            {"title": "A vector: a list and an arrow", "image": I("vectors_arrows.png"),
             "bullets": ["[3, 2] = 3 steps right, 2 up", "Each position has a fixed meaning", "Add: tip to tail", "Scale: stretch or flip", "Length: Pythagoras"],
             "notes": "Treasure map analogy: the list is the written directions, the arrow is the path on the map. Show adding tip to tail and scaling. Length of [3, 4] is 5. Ask a student to compute the length of [6, 8]. Answer: 10."},
            {"title": "Dot product: multiply pairs, then add",
             "bullets": ["a . b = one single number", "A shopping receipt is a dot product", "Weighted sum = dot product", "A neuron = weighted sum + squash"],
             "code": "qty   = np.array([2, 1, 3])\nprice = np.array([799, 2499, 249])\nqty @ price   # 4844 = total bill",
             "notes": "Start with the receipt: quantities times prices, added up. Everyone has done a dot product. Then the final-grade example with weights 0.5, 0.3, 0.2. Tell them a neuron in a neural network does exactly this, so networks are mostly dot products."},
            {"title": "The sign of the dot product", "image": I("dot_product_angles.png"),
             "bullets": ["Positive: similar direction", "Zero: right angle, unrelated", "Negative: opposite", "Two people pushing a box"],
             "notes": "Two people pushing a box: same direction, efforts add; at right angles, neither helps the other's direction; against each other, they cancel. Read the numbers under each panel."},
            {"title": "Cosine similarity and embeddings", "image": I("word_vectors_2d.png"),
             "bullets": ["Dot product / (length a x length b)", "From -1 to +1; direction only", "Similar meaning -> similar direction", "Powers semantic search and RAG"],
             "notes": "Compass analogy: we do not care how big the compass is, only where the needle points. Real embeddings have hundreds of numbers; this is a 2-D toy. cat and dog score near 1, cat and truck near 0. Notebook 01 builds a tiny semantic search."},
            {"title": "Matrix = table of data", "bullets": ["Rows = examples, columns = features", "Shape: rows x columns", "Transpose flips rows and columns", "Matrix @ vector = a dot product per row"],
             "code": "scores = np.array([[80, 72, 65],\n                   [65, 90, 70],\n                   [70, 88, 92]])\nweights = np.array([0.5, 0.3, 0.2])\nscores @ weights  # [74.6 73.5 79.8]",
             "notes": "A matrix is the X of machine learning: one row per example, one column per feature. Multiplying by the weight vector gives every student's final grade at once. Check one row by hand together."},
            {"title": "Matrix multiplication, visually", "image": I("matmul_visual.png"),
             "bullets": ["Cell (i, j) = row i of A . column j of B", "(m x n) @ (n x p) -> (m x p)", "Inner numbers must match", "A @ B is usually not B @ A"],
             "notes": "Point at the highlighted row and column and compute 3 times 9 plus 4 times 12 equals 75. Then the restaurant bill analogy: tables times dishes, dishes times price and calories, gives tables times price and calories. The dishes dimension must match and disappears. Shape errors are the most common deep-learning bug."},
            {"title": "A matrix moves space", "image": I("matrix_transform.png"),
             "bullets": ["Scale, rotate, shear", "Every point moves together", "A network layer = X @ W + b", "Layers reshape data until the task is easy"],
             "notes": "Each 2 by 2 matrix moves the whole grid. Neural network layers do this in many dimensions, learning matrices that move the data into a space where, for example, cats and dogs separate. The one line X at W plus b is a whole layer."},
            {"title": "Probability and distributions", "image": I("distributions.png"),
             "bullets": ["0 = impossible, 1 = certain", "All outcomes add up to 1", "Uniform, normal (bell), binomial", "LLMs: a probability for every word"],
             "notes": "Flip a virtual coin 10 times and then 5000 times in notebook 03 to show the law of large numbers. Describe each histogram. Mention the categorical distribution: an LLM gives a probability to every token in its vocabulary."},
            {"title": "Mean, variance, standard deviation", "image": I("mean_variance.png"),
             "bullets": ["Mean = centre", "Variance = average squared distance from mean", "Std = square root, same units", "About 68% within 1 std (normal)"],
             "notes": "Two archers analogy: both average the bullseye, but one is scattered. The mean alone hides spread. Work the small example [4, 8, 6, 5, 7] on the board: mean 6, variance 2, std about 1.41."},
            {"title": "Softmax and temperature", "image": I("softmax_temperature.png"),
             "bullets": ["Logits -> exp -> divide by total", "Positive, sums to 1", "Low T: sharp, predictable", "High T: flat, varied", "This is the API 'temperature'"],
             "notes": "Work [2, 1, 0.1] to [0.66, 0.24, 0.10]. Then show the three temperatures. Talent show analogy: at low temperature the winner takes almost all the prize money. Open the Softmax sheet in the spreadsheet and change the temperature cell live."},
            {"title": "Derivative = slope at a point", "image": I("derivative_slope.png"),
             "bullets": ["Slope = rise / run", "Curve: slope changes along it", "Estimate: (f(x+h) - f(x)) / h", "Sign tells you which way is downhill"],
             "notes": "Foggy hillside analogy: you cannot see the valley but you can feel the tilt under your feet. That tilt is the derivative. Show the numerical derivative of x squared at 3 approaching 6 as h shrinks."},
            {"title": "Loss functions: one number for 'how wrong'", "image": I("loss_functions.png"),
             "bullets": ["MSE for numbers", "Big errors cost much more", "Cross-entropy for categories", "-log(p of the correct answer)"],
             "notes": "Lower loss is better; training means making it small. Probability 0.9 on the right answer costs 0.105, probability 0.01 costs 4.6. LLMs are trained with cross-entropy on the next token."},
            {"title": "Gradient descent, frame by frame", "image": I("gd_strip.png"),
             "bullets": ["new w = w - lr x slope", "Steps shrink as slope flattens", "Frames in images/gd_frames/"],
             "notes": "Walk through the frames left to right like a flip-book. At step 0 the slope is minus 8 so w jumps right by 1.6. The steps get smaller automatically as the curve flattens. You can also put the eight separate frame images on consecutive slides for an animation effect."},
            {"title": "The training loop", "image": I("training_loop.png"),
             "bullets": ["Predict", "Measure loss", "Compute gradient", "Update weights", "Repeat"],
             "notes": "This loop is how every neural network learns, from a line fit to a large language model. The gradient is the list of slopes, one per weight. In PyTorch, autograd computes it for you."},
            {"title": "Learning rate: the step size", "image": I("learning_rates.png"),
             "bullets": ["Too small: crawls", "About right: smooth", "Too large: overshoots, diverges", "Try it: Gradient descent sheet"],
             "notes": "Open the spreadsheet's Gradient descent sheet and change the learning rate from 0.1 to 0.9 and then 1.1. At 1.1 the w column explodes. This is the most memorable demo of the session."},
            {"title": "Common mistakes",
             "bullets": ["Mixing up dot product and element-wise *", "Ignoring shapes before @", "Forgetting softmax sums to 1", "Adding the gradient instead of subtracting",
                         "Learning rate far too big", "Reading correlation or similarity as 'same'"],
             "notes": "Go through each and ask students which one they think they would make. Fixes are in trainer-notes.md."},
            {"title": "Recap and exercises",
             "bullets": ["Vectors, dot product, cosine similarity", "Matrices: tables and transformations", "Probability, mean/variance, softmax",
                         "Derivatives, gradients, gradient descent, loss", "Now: exercises.md and the spreadsheet"],
             "notes": "One sentence per idea, then set exercises 1 to 5 in class and the rest as homework. Remind them all notebooks run offline."},
        ],
    }


def main():
    mermaid_diagrams()
    figures.all_figures()
    print("images written")
    for name, cells in all_notebooks().items():
        notebook(cells, HERE / "notebooks" / name)
    print("notebooks written")
    excel()
    slides(deck(), HERE / "slides" / "03-math-for-ai.pptx")
    pdf_from_markdown(HERE / "concepts.md", HERE / "pdf" / "03-math-for-ai-handout.pdf", title="Module 03 - Math for AI")
    print("excel, slides, pdf written")


if __name__ == "__main__":
    main()
