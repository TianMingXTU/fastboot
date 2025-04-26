from fastboot.application import FastBootApp

if __name__ == "__main__":
    app = FastBootApp()
    app.run()  # 现在可以不传参数，将使用配置文件中的值
