# Module 02 — Resources

Links chosen from the course's curated source lists (see the repo's `SOURCES.md`) plus official documentation. Each line says why it is worth your time. Start with the three official docs; use the rest for extra practice.

## Official documentation (keep these open)
- [NumPy documentation](https://numpy.org/doc/stable/) — the reference for arrays, broadcasting and vectorised maths; the "absolute beginners" guide in the user section is a good second read after notebook 01.
- [pandas documentation](https://pandas.pydata.org/docs/) — the official user guide for loading, cleaning, merging and grouping. Check here when a tutorial uses an older pandas style (this module uses pandas 3.0).
- [Matplotlib documentation](https://matplotlib.org/stable/) — includes a large gallery of example charts you can copy and adapt.
- [scikit-learn](https://scikit-learn.org/stable/) — its built-in `load_*` datasets (iris, wine, diabetes and others) work offline, ideal for extra pandas practice and for Module 04.

## Quick references
- [pandas cheat sheet (PDF)](https://github.com/pandas-dev/pandas/blob/master/doc/cheatsheet/Pandas_Cheat_Sheet.pdf) — the pandas team's own two-page visual summary of reshaping, filtering and grouping. Pairs well with our `excel/pandas-cheatsheet.xlsx`.
- [CS231n Python & NumPy tutorial](http://cs231n.github.io/python-numpy-tutorial/) — a crisp one-page NumPy primer written for people heading towards deep learning.

## Learn more, step by step
- [Python Data Science Handbook](https://github.com/jakevdp/PythonDataScienceHandbook) — a free book as notebooks covering NumPy, pandas and Matplotlib in one consistent style; the best next step after this module.
- [Kaggle Learn](https://www.kaggle.com/learn/overview) — short, free pandas, data-visualisation and data-cleaning micro-courses with auto-checked exercises in the browser.
- [pandas tutorial (Kaggle notebook)](https://www.kaggle.com/junaaaaloo/pandas-tutorial) — a runnable notebook you can copy and experiment with online.
- [Summarising, aggregating and grouping in pandas](https://www.shanelynn.ie/summarising-aggregation-and-grouping-data-in-python-pandas/) — worked `groupby` examples, the topic where most beginners get stuck.
- [Intro to Python for Data Science (DataCamp)](https://www.datacamp.com/courses/intro-to-python-for-data-science) — interactive in-browser exercises (freemium) for learners who like instant feedback.
- [Applied Data Science with Python (Coursera)](https://www.coursera.org/specializations/data-science-python) — a longer structured track (free to audit) covering plotting, ML, text and networks.

## Datasets for your own EDA practice
- [UCI Machine Learning Repository](https://archive.ics.uci.edu/datasets) — classic small, well-documented tables. Download once, then work offline.
- [Kaggle datasets and competitions](https://www.kaggle.com/) — thousands of real datasets, each with public notebooks showing how others explored them.

## Examples and roadmaps
- [Data Analysis & ML Projects (rhiever)](https://github.com/rhiever/Data-Analysis-and-Machine-Learning-Projects) — example notebooks of end-to-end exploratory analysis done well; good models for Exercise 12.
- [OSSU Data Science curriculum](https://github.com/ossu/data-science) — a self-taught roadmap showing where data skills sit in a full curriculum.
- [5 web scraping projects with Python](https://amankharwal.medium.com/5-web-scraping-projects-with-python-4bcc25ff039) — ideas for collecting your own data (Medium may limit free reads); useful later for RAG and automation projects.

## Notes for trainers
- Library versions change: this module was built with NumPy 2.5 and pandas 3.0 (late 2026). If a student's code from an older tutorial behaves differently (for example `inplace=True` on a column), check the pandas documentation's "Copy-on-Write" page.
- The practice data in this module is synthetic; any real dataset you bring in should be checked for personal data before sharing with students.
