<center><h2>🚀 Langchain-Deepseek: Using the deepseek model in langchain</h2></center>
## Install

* Install from source (Recommend)

```bash
cd langchain-deepseek
pip install -e .
```
* Install from PyPI
```bash
pip install langchain-deepseek
```

## Quick Start
* All the code can be found in the `examples`
* Set DeepSeek API key in environment if using DeepSeek models: `export DEEPSEEK_API_KEY="sk-...".`
*  Maybe you can try loading environment variables like this. Create a new `.env` file
```
DEEPSEEK_API_KEY="sk-..."
```
```python
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
```
##### It works with the Langchain library

```python
from langchain_deepseek import ChatDeepSeekAI
from langchain_core.output_parsers import StrOutputParser

llm = ChatDeepSeekAI(
    model="deepseek-chat",
    api_key="sk-...",
)

output_parser = StrOutputParser()
chain = llm | output_parser
response = chain.invoke("太阳系有几大行星？")
print(response)
```



## 🌟Citation

```python
@article{guo2025langchain-deepseek,
title={langchain-deepseek: Using the deepseek model in langchain},
author={Runke Zhong},
year={2025}
}
```
**保持热爱，奔赴星海！**

*这个世界上唯有两样东西能让我们的心灵感到深深的震撼：一是我们头上灿烂的星空，一是我们内心崇高的道德法则*
