import setuptools
 
with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()
 
setuptools.setup(
    name="pylwr",  # 项目名称，保证它的唯一性，不要跟pypi上已存在的包名冲突即可
    version="1.1.2",  # 程序版本
    # py_modules=['mysql'],  # 需要上传的模块名称，这样可以让这些模块直接import导入
    author="linwr",  # 项目作者
    author_email="953297255@qq.com",  # 作者邮件
    description="各种包使用的二次封装",  # 项目的一句话描述
    long_description=long_description,  # 加长版描述
    long_description_content_type="text/markdown",  # 描述使用Markdown
    url="https://gitee.com/linwanrui/pylwr",  # 项目地址
    packages=setuptools.find_packages("src"),  # 无需修改
    package_dir = {"":"src"},		# 告诉 setuptools 包都在 src 下
    package_data = {
    ## 包含 data 文件夹下所有的 *.dat 文件
        "":[".txt", ".info", "*.properties", ".py"],
        "":["data/*.*"],
    },
    # 取消所有测试包
    exclude = ["*.test", "*.test.*", "test.*", "test"]
    # install_requires=['docutils>=0.3'], # 依赖包增加
)