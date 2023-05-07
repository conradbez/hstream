# Static files

HStream exposes the underlying FastAPI app to the developer, this allows for great flexibility as your app grows.

One of the big painpoints we've add with alternatives (for example Streamlit) is how hard it is to host static files. With HStream you can simple:

```
from hstream import hs

hs.app.mount("/static", StaticFiles(directory="static"), name="static")
```

Now we're hosting our folder `static` on the HStream instance of FastAPI app and can be accessed at `http://127.0.0.1:8080/static/test.html`.


Have a look at how intuitive this is by simply following the [FastAPI documentation](https://fastapi.tiangolo.com/tutorial/static-files/) on static files.