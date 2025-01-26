# 📝 Streamlit Ace

[![GitHub][github_badge]][github_link] [![PyPI][pypi_badge]][pypi_link] 

## Installation

```sh
pip install streamlit-ace
```

## Getting started

```python
import streamlit as st 

from streamlit_ace_cursor import st_ace

st.write("Hello World")
code = st_ace(auto_update=False)

code 

code2 = st_ace(auto_update=True)

code2
```

## Demo

[![Open in Streamlit][share_badge]][share_link] 

[![Preview][share_img]][share_link]

[share_badge]: https://static.streamlit.io/badges/streamlit_badge_black_white.svg
[share_link]: https://share.streamlit.io/okld/streamlit-gallery/main?p=ace-editor
[share_img]: https://raw.githubusercontent.com/okld/streamlit-ace/main/preview.png

[github_badge]: https://badgen.net/badge/icon/GitHub?icon=github&color=black&label
[github_link]: https://github.com/okld/streamlit-ace

[pypi_badge]: https://badgen.net/pypi/v/streamlit-ace?icon=pypi&color=black&label
[pypi_link]: https://pypi.org/project/streamlit-ace
