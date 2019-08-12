@[TOC](某版本瑞数解决方案-爬虫)

# 前言

本次采集的目标站点是`江苏省农村产权交易信息平台`，网址`http://www.jsnc.gov.cn/jygg/tzgg/index.html`。没想到这么小的网站都上瑞数了，爬虫真是越来越难了。回归正题，该网站的防御机制是在`cookie`上做了手脚，`cookie`名称为`YwnBCHQI8xgWI5a`。

# 工具
 1. `Chrome`浏览器（方便调试）
 2. `Node.js`开发环境（JS代码运行）
 3. `Python`开发环境
 4. `VSCode`(代码阅读)


# 分析过程

## JS获取
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190812235800268.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0NzMxNjI3,size_16,color_FFFFFF,t_70)
这段代码就是获取产生cookie的代码了，进去打断点调试，发现我还是想的太简单了，每次请求这个代码链接。代码都是动态的，打的断点都乱掉了。通过反复观察，代码内容都是一样的，只不过就是打乱了顺序而已。不像高级的版本，比如`托福`这个网站，版本比较高级。既然打乱了顺序，咱们就把代码复制下来自己搭建一个web服务慢慢调试。
- 这里使用了 `python -m http.server` 这个功能，只要当前目录下有`index.html`文件即可，自己复制`index.html` 以及`a6a1a7`js文件，需要修改`index.html` 中js文件的路径。

## js代码分析
1. 该代码开始首先会将一些方法，对象进行混淆。
```javascript
    var _$lz;
    var _$lE = window;
    var _$ks = {};
    var _$lf = Math;
    var _$bV = Math.ceil;
    var _$go = String;
    var _$kx = _$go.fromCharCode;
    var _$lD = document;
    var _$ac = location;
    var _$lp = _$lE.Array;
    var _$cB = eval
```
2. 定位到 `cookie`生成的函数
```javascript
    function _$kP() {
        if (_$jb - _$la() < 0) {
            return _$kN;
        }
        // cookie名称 YwnBCHQI8xgWI5a
        var _$a7 = _$gT();
        // k
        var _$dh = _$ks._$gc();
        var _$iC = _$ai();
        var _$gi = _$h1();
        // 该方法会验证当前浏览器环境。以及计算出浏览器的唯一指纹
        var _$c1 = _$aU();
        // 拿着计算出来的一堆参数再去计算最终cookie值 哈哈哈好绕啊。
        var _$hp = _$dh + _$gI(_$gi[_$ks._$h5()](_$eO(_$c1, _$iC)));
        // 设置cookie
        _$ja(_$a7, _$hp, 7, _$ks._$gN(), _$ks._$gN());
        // cookie 名称和值进行拼接
        _$kN = _$a7 + _$ks._$fP() + _$hp;
        return _$kN;
    }
```
3. 找到入口函数就好办了，扣出来用`Node.js` 执行
4. 计算`cookie` 中还有一个坑就是他会根据js中的 _$g0 函数返回的一堆字符串的进行计算
```javascript
    function _$g0() {
        // 其实是一些网站的信息，加密了。
        // 解密出来的值为 "`cookieKey:BTvo5JQ7qt6M3G1jLKRleWXwFuJvWI20fJ.j_LnK1E7`blackBlock:lpkqiYeztiqEjarN.AU.jG`refreshInterval:10`protectedSites:;http://221.226.99.21:80;http://221.226.99.22:80;http://221.226.99.23:8000;http://www.jsic.gov.cn:80;http://www.jsic.gov.cn:8000;http://www.jsnc.gov.cn:80;http://www.qunzh.com:80;`resPath:/mRnE3GFBhtb7/`tokenTimeout:1800`tokenUsedThreshold:50`switchFlags:06c"
        return "ujmyyuso3oaVx_5/6r6.n=)qJa:N6L5/5zT)7QrJ=u=ks+U1L?3swzOjlvkmu*vymuV-k6m6_0qLz7~8N8l2]+<b/j|op|o}r1x~o|^kvVMLjz|y~om~on;s~o}VWr~~zVKKNNMJNNRJUUJNMVTLWr~~zVKKNNMJNNRJUUJNNVTLWr~~zVKKNNMJNNRJUUJNOVTLLLWr~~zVKK___Jt}smJqy^JmxVTLWr~~zVKK___Jt}smJqy^JmxVTLLLWr~~zVKK___Jt}xmJqy^JmxVTLWr~~zVKK___J{]xbrJmywVTLWj|o}8k~rVKw:x-O/.*r~lSKj~yuox<swoy]~VMTLLj~yuox=}on<r|o}ryvnVQLj}_s~mr.vkq}VLPR";
    }
```
5. 到这里算是差不多的坑都踩完了吧。最后就是调js哪里不行补哪里。



有什么问题需要探讨的可以 + qq_vx: `240942649` 
