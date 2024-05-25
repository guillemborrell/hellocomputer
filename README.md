# hellocomputer

[Hello, computer!](https://youtu.be/hShY6xZWVGE?si=pzJjmc492uLV63z-)

`hellocomputer` is a GenAI-powered web application that allows you to analyze spreadsheets 

![gui](./docs/img/gui_v01.png)


## Quick install and run

If you have `uv` installed, just clone the repository and run:

```
uv pip install -r requirements.in
```

And to get the application up and running...

```
uvicorn hellocomputer.main:app --host localhost
```
