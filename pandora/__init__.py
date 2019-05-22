from flask import Flask
from flask import render_template
from flask import jsonify



def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        """
        只有 Hello World 的首页
        :return:
        """
        return "Hello, world!"

    # TODO: 捕获 404 错误，返回 404.html
    @app.errorhandler(404)
    def page_not_found(error):
        """
        以此项目中的404.html作为此Web Server工作时的404错误页
        """
        return render_template('404.html'), 404

    # TODO: 完成接受 HTTP_URL 的 picture_reshape
    # TODO: 完成接受相对路径的 picture_reshape
    @app.route('/pic', methods=['GET' ])
    def picture_reshape():
        """
        **请使用 PIL 进行本函数的编写**
        获取请求的 query_string 中携带的 b64_url 值
        从 b64_url 下载一张图片的 base64 编码，reshape 转为 100*100，并开启抗锯齿（ANTIALIAS）
        对 reshape 后的图片分别使用 base64 与 md5 进行编码，以 JSON 格式返回，参数与返回格式如下
        
        :param: b64_url: 
            本题的 b64_url 以 arguments 的形式给出，可能会出现两种输入
            1. 一个 HTTP URL，指向一张 PNG 图片的 base64 编码结果
            2. 一个 TXT 文本文件的文件名，该 TXT 文本文件包含一张 PNG 图片的 base64 编码结果
                此 TXT 需要通过 SSH 从服务器中获取，并下载到`pandora`文件夹下，具体请参考挑战说明
        
        :return: JSON
        {
            "md5": <图片reshape后的md5编码: str>,
            "base64_picture": <图片reshape后的base64编码: str>
        }
        """

        import base64
        import requests
        import hashlib
        import os
        from PIL import Image
        from io import BytesIO
        from flask import request
        b64_url = request.args.get('b64_url')
        if 'http' not in b64_url:
            filename = os.path.join(app.root_path, 'static', b64_url)
            with open(filename, 'r') as f:
                b64 = f.read()
        else:
            r = requests.get(url=b64_url)
            b64 = r.text
        img_data = base64.b64decode(b64)
        img_data = BytesIO(img_data)
        img = Image.open(img_data)
        img = img.resize((100, 100),Image.ANTIALIAS)
        output_buffer = BytesIO()
        img.save(output_buffer, format='PNG')
        byte_data = output_buffer.getvalue()
        base64_str = base64.b64encode(byte_data)
        md5_data = hashlib.md5()
        md5_data.update(byte_data)
        # m2 = hashlib.md5()
        # m2.update(img.tobytes())
        # print(m2.hexdigest())
        md5_str =md5_data.hexdigest()
        res = jsonify({"md5":md5_str,"base64_picture":str(base64_str,encoding="UTF-8")})
        return res




    # TODO: 爬取 996.icu Repo，获取企业名单
    @app.route('/996')
    def company_996():
        """
        从 github.com/996icu/996.ICU 项目中获取所有的已确认是996的公司名单，并

        :return: 以 JSON List 的格式返回，格式如下
        [{
            "city": <city_name 城市名称>,
            "company": <company_name 公司名称>,
            "exposure_time": <exposure_time 曝光时间>,
            "description": <description 描述>
        }, ...]
        """
        import requests
        import re
        r = requests.get('https://github.com/996icu/996.ICU/tree/master/blacklist/README.md')
        res_tr = r'<tr>(.*?)</tr>'
        m_tr = re.findall(res_tr, r.text, re.S | re.M)
        cont = []
        for line in m_tr:
            res_td = r'<td align="center">(.*?)</td>'
            m_td = re.findall(res_td, line, re.S | re.M)
            for j in m_td:
                cont.append(j)
        c = []
        reg = re.compile('<[^>]*>')
        for i in cont:
            c.append(reg.sub('', i))
        cont = c
        for i in range(len(cont)):
                if cont[i] == '盖章文件':
                    s = i + 1
                    break
        # for i in range(len(cont)-1,-1, -1):
        #     if cont[i] == '-->':
        #         e = i
        #         break
        cont = cont[s:]
        city = []
        company = []
        exp = []
        des = []
        for i in range(len(cont)):
            if i % 5 == 0:
                city.append(cont[i])
            elif i % 5 == 1:
                company.append(cont[i])
            elif i % 5 == 2:
                exp.append(cont[i])
            elif i % 5 == 3:
                des.append(cont[i])

        res = []
        for i in range(len(des)):
            res.append({"city": city[i],"company": company[i],"exposure_time": exp[i],"description": des[i]})
        res = jsonify(res)
        return res

    return app
