<div align="center">
  <h1><b>colab-assist</b></h1>
  <p>
    Utilities that assist development workflows on Google Colab
  </p>

  <h4>
    <a href="https://colab-assist.readthedocs.io">Documentation</a>
  <span> · </span>
    <a href="https://github.com/dd-n-kk/colab-assist/issues/">Issues</a>
  <span> · </span>
    <a href="https://pypi.org/project/colab-assist/">PyPI</a>
  </h4>
</div>


## About

- __colab-assist__ is a small package that shares utility functions
  I find useful for my development workflows on [Google Colab](https://colab.google).

- Actually, this is also a semi-mock project that I use to learn Python open-source development.
  [Feedbacks, guidance, and feature suggestions](https://github.com/dd-n-kk/colab-assist/issues/)
  are much appreciated!


## Usage

### Experimenting your private Python package on Colab

1. Develop your package any way you like and push it to your private GitHub repo.

2. Make a repo-specific [personal access token (PAT)](https://is.gd/qWZkuT).

3. Store the PAT as a [Colab Secret](https://stackoverflow.com/a/77737451):

    ![Colab Secrets demo](assets/imgs/colab_secrets.png)

4. On Colab:
    ```py
    import colab_assist as A
    ```

    - Install → experiment → push → resintall:
      ```py
      # Install your private package
      A.install_gh("me/my_pkg", "dev", secret="my_token")

      # Experiment
      from my_pkg import foo
      foo()

      # (Push update accordingly to the development branch of your repo)

      # Reinstall updated package
      A.install_gh("me/my_pkg", "dev", secret="my_token")

      # Reimport updated functions/classes without needing to restart Colab session
      foo = A.reload(foo)
      foo()
      ```

    - Or clone → experiment → push → pull:
      ```py
      # Clone your private package and add it to `sys.path`
      A.clone_gh("me/my_pkg", "dev", opt="p", secret="my_token")

      # Experiment
      from my_pkg import foo
      foo()

      # (Push updates accordingly to the development branch of your repo)

      # Pull the update
      A.pull_gh("my_pkg")

      # Reimport updated functions/classes without needing to restart Colab session
      foo = A.reload(foo)
      foo()
      ```


## Dependencies & Installation

- Although currently colab-assist lists no dependency,
  it is intended to __only be installed and used in a Google Colab environment__.
  The reason not to explicitly list dependencies for now is that
  at least one depedency ([`google-colab`](https://github.com/googlecolab/colabtools))
  is bespoke for Colab and not hosted on PyPI.
  However, colab-assist is designed to install and run just fine on a fresh Colab instance.

- You can install colab-assist very quickly with the pre-installed uv on Colab:
  ``` { .yaml .copy }
  !uv pip install --system -qU colab-assist
  ```
  Or with pip:
  ``` { .yaml .copy }
  %pip install -qU colab-assist
  ```

- This package is currently a single-file package.
  Therefore you may use it quick and dirty by just downloading the module file:
  ``` { .yaml .copy }
  !wget -q https://raw.githubusercontent.com/dd-n-kk/colab-assist/master/src/colab_assist/colab_assist.py
  ```


## License

- [MIT license](https://github.com/dd-n-kk/colab-assist/blob/main/LICENSE)


## Acknowledgements

- [uv](https://github.com/astral-sh/uv)
- [MkDocs](https://github.com/mkdocs/mkdocs)
- [Material for MkDocs](https://github.com/squidfunk/mkdocs-material)
- [mkdocstrings](https://github.com/mkdocstrings/mkdocstrings)
- [Awesome Readme Template](https://github.com/Louis3797/awesome-readme-template)
