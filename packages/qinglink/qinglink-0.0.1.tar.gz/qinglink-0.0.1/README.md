# aiop

一个AI脚本集，正在开发中


## 获取模型文件的模型信息（civitai）

```shell
aiop info -p path/to/your/file
```

- `-p` 要获取信息的文件路径

## 获取当前文件夹下所有模型文件的预览图并且按名字保存到当前目录

```shell
aiop preview -p path/to/the/dir -r
```

- `-p` 要获取预览图的文件夹路径
- `-r` 是否递归子文件夹

## 给当前文件夹下所有模型文件进行分类

> [!tip]
> 这个函数还不是很好，最好只用一次，第二次会出现文件夹套文件夹很不美观，待优化

```shell
aiop classify -p path/to/the/dir -r
```

- `-p` 要分类的文件夹路径
- `-r` 是否递归子文件夹
- `-a` 遇到没有预览文件的模型是否自动下载预览图片