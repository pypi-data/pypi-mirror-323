import setuptools  # 导入setuptools打包工具

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lingmopyui",  
    version="1.0.11", 
    author="Admibrill",  
    author_email="admibrill@outlook.com", 
    description="A Lingmo GUI Library based on PySide6.QtWidgets",  
    long_description=long_description,  
    long_description_content_type="text/markdown",
    url="https://github.com/LingmoOS/LingmoPyUI",  
    packages=setuptools.find_packages(),
    data_files=[('Lib/site-packages/LingmoPyUI/Font', ['./LingmoPyUI/Font/FluentIcons.ttf']),
                ('Lib/site-packages/LingmoPyUI/Image', ['./LingmoPyUI/Image/btn_close_hovered.png',
                                                    './LingmoPyUI/Image/btn_close_normal.png',
                                                    './LingmoPyUI/Image/btn_close_pushed.png',
                                                    './LingmoPyUI/Image/btn_max_hovered.png',
                                                    './LingmoPyUI/Image/btn_max_normal.png',
                                                    './LingmoPyUI/Image/btn_max_pushed.png',
                                                    './LingmoPyUI/Image/btn_min_hovered.png',
                                                    './LingmoPyUI/Image/btn_min_normal.png',
                                                    './LingmoPyUI/Image/btn_min_pushed.png',
                                                    './LingmoPyUI/Image/icon.png',
                                                    './LingmoPyUI/Image/noise.png',]),],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # 对python的最低版本要求
)