# griffe-generics
![Build status](https://github.com/jonghwanhyeon/griffe-generics/actions/workflows/publish.yml/badge.svg)

A Griffe extension that resolves generic type parameters as bound types in subclasses

## Example
Without extension:
![Without Extension](https://github.com/jonghwanhyeon/griffe-generics/raw/main/assets/without-extension.png)

With extension:
![With Extension](https://github.com/jonghwanhyeon/griffe-generics/raw/main/assets/with-extension.png)

## Install
To install **griffe-generics**, simply use pip:

```console
$ pip install griffe-generics
```

## Usage
```yaml
plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            extensions:
              - griffe_generics
```
