# leversion ![](https://github.com/lework/leversion/workflows/checkVersion/badge.svg) ![GitHub](https://img.shields.io/github/license/lework/leversion) 

> 列出开源软件的最新版本(List the latest version of open source software)

## Build Setup

``` bash
# install dependencies
npm install

# serve with hot reload at localhost:8080
npm run dev

# build for production with minification
npm run build

# build for production and view the bundle analyzer report
npm run build --report

```

## 生成数据

> 每天凌晨6点更新数据

* `scripts/source.json`  记录要搜集版本的开源软件列表
* `static/data/data.json`  存放搜集到的数据

``` bash
# 使用脚本生成数据

python3 scripts/check.py
```

## 参与贡献

欢迎任何形式的贡献.
