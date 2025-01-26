# models.py
from dataclasses import dataclass

@dataclass
class PageContent:
    url: str
    title: str
    content: str

# Burada isterseniz başka modelleri de tanımlayabilirsiniz
