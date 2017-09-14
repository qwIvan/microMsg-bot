# microMsg-bot
微信表情机器人，接口来自 doutula

## 使用方法
前往 [bot.libivan.com](http://bot.libivan.com)，打开手机微信用摄像头扫描二维码登录。

## 后缀发表情
效果图：

![效果图](https://user-images.githubusercontent.com/7613160/30426397-790f14da-997e-11e7-8738-bb066fea77d6.png)

![效果图](https://user-images.githubusercontent.com/7613160/30423776-7a3519de-9976-11e7-81c2-5512fb906994.png)


## 被@回复表情
效果图：

![效果图](https://user-images.githubusercontent.com/7613160/30422855-b83876c0-9973-11e7-8a95-aefa4a0669b0.png)

![效果图](https://user-images.githubusercontent.com/7613160/30422854-b8371384-9973-11e7-97d4-f9f6cdb29496.png)


## 挂机
网页版微信每次离线后，都要扫二维码才能重新登录，因此可以用服务器挂着账号来维持session。

在bot.libivan.com成功登录后打开chrome控制台可以看到如图所示的log：
![图示](https://user-images.githubusercontent.com/7613160/30424325-2a5e5b12-9978-11e7-8042-8e1f4298ab55.png)

复制黄框内容，前往红线链接，在新打开的窗口控制台中粘贴进去执行，便可同时使用网页版微信和机器人。
![图示](https://user-images.githubusercontent.com/7613160/30424548-da97d562-9978-11e7-9c65-48680a4cf9cd.png)

当网页版微信离线后只需要刷新或者重新执行代码便可脱离手机使用网页版微信。

## 部署

### 简易方式
```
docker run -p 80:80 -e KEY=YOUR_SECRET_KEY qwivan/micromsg-bot
```

### 使用 docker volume
```
docker volume create mmbot
docker run -t -p 80:80 -e KEY=YOUR_SECRET_KEY -v mmbot:/data qwivan/micromsg-bot
```
