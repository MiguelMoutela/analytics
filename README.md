# Analytics

# Prerequisites

Install with the appropriate package for your operating system. For example, Mac users may want to use [`homebrew`](https://brew.sh/).

- [Python 3](https://www.python.org/downloads/)
- [`pip`](https://pip.pypa.io/en/stable/installing/)
- [Jupyter Notebook](http://jupyter.org/install.html)

Install required Python packages for these notebooks using the `pip` command.

```bash
pip install -r requirements.txt
```

**Or**, if using Homebrew:

```bash
pip3 install -r requirements.txt
```

# Installation

Clone this repository.

```bash
git clone https://github.com/all-of-us/analytics.git
cd analytics
```

Enable pre-commit hooks for code consistency.

```bash
git config core.hooksPath hooks/
```

# Running the Notebooks

```bash
cd notebooks
jupyter notebook
```

# Development

1. **Carefully review code to ensure it does not contain exported data.**
1. Use a new feature branch when committing and pushing code to GitHub.
1. Open a Pull Request to merge your branch back into `master`.
1. Merge the Pull Request after it is reviewed by another team member.

# Troubleshooting

**Missing module in notebook** - Ensure you are running the Python 3 version of `pip` against the `requirements.txt` file to install packages. For example, you may need to replace `pip` with `pip3` to install it correctly.
