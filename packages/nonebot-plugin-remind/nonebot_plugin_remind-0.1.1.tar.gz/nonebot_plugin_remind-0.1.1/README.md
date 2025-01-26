<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>
<div align="center">
  
# nonebot-plugin-remind

</div>

## 📖 介绍

这是一个提供符合中国宝宝体质的定时提醒功能的插件

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-remind

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

**pip**

    pip install nonebot-plugin-remind

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_remind"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加如下可选配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| `private_list_all` | 否 | `Ture` | 私聊中"/提醒列表"命令是否列出私聊群聊全部提醒 |
| `remind_keyword_error` | 否 | `Ture` | 触发“提醒”关键词时是否发送错误提示 |

## 🎉 使用

### 关键词触发

#### 提醒
触发格式：
> [@][时间]'提醒'[被提醒人][消息]

各部分解释：
- **[@]**（以下条件任意满足一条即可）
    - 在消息开头@机器人
    - 回复机器人的任意一条消息
    - 如果机器人设置了 `NICKNAME` 环境变量，则只需在消息开头称呼其昵称

- **[时间]**（以下时间格式均符合要求）：必须使用**北京时间24小时制**
    - `2025-1-1-8:00`: 精确设定2025年1月1日上午8:00
    - `9.10.18:00` 或者 `9.10.18.00`: 设定距离当前时间最近的未来的9月10日18:00
    - `21:12` 或者 `21.12`: 设定距离当前时间最近的未来的21点12分

- **'提醒'**： 要匹配的关键字，必须完全一致

- **[被提醒人]**（以下格式均符合要求）
    - `我`：提醒设定提醒的人自己
    - `[@]`:可以@多个用户，包括自己，也可以@全体成员
    - `我和[@]`：必须我在前面，其他@用户在后 
    - `all` 或者 `所有人`: 等同于`@全体成员`，提供一个非打扰式的提醒设定 

- **[消息]**
    - 任意消息（支持图片、QQ黄脸表情等富文本消息）均可，前提是必须在同一条消息中发送出


示例：
1. `@机器人 16:00提醒我去开会`
2. `机器人昵称，1.1.11.40提醒所有人去聚餐`
3. `机器人昵称 2025-1-29-8:00提醒我和@用户1 用户2 新年新气象！`
4. **错误示例：** `@机器人 明天16:00提醒我去开会`，此时默认情况机器人会报错，配置环境变量 `remind_keyword_error=false` 可关闭匹配错误时的提醒。

### 指令触发
以下触发均需要指令前缀，如未设置默认未`/`。

#### 提醒

- 提供1个参数为 `被提醒人`，以交互的方式设置提醒：

- 提供3个参数，以英文逗号`,`间隔，依次为：`被提醒人`，`时间`和`提醒消息`：

> 以上两种命令的触发方式均可省略 `被提醒人` 参数，省略时默认被提醒人为“我”。

#### 提醒列表

**列表顺序默认按提醒时间顺序排序，使用 `-s` 选项按设置提醒的先后顺序排序**

当在群聊中触发此指令时，仅返回在群聊内设置的提醒。

当在私聊中触发此指令时，返回所有私聊和群聊中设置的提醒。

**注意**：当配置环境变量 `private_list_all=false` 时，私聊时也仅返回私聊中设置的提醒。

#### 删除提醒

**使用的列表顺序默认按提醒时间顺序排序，使用 `-s` 选项按设置提醒的先后顺序排序的序号删除**

> 注意：在删除提醒之前一定要先通过 `/提醒列表` 指令查看序号！每次删除后后续序号都会更新！

示例：
1. `/删除提醒 1`：删除序号为1的提醒（默认按提醒时间排序）
2. `/删除提醒 -s 1-3 5`：批量删除序号为1、2、3、5的提醒（按设置时间排序）
3. `/删除提醒 all`：一键删除所有提醒（仅当前群聊）

### 示例图

<table style="width:100%; border-collapse: collapse;">
  <thead>
    <tr style="border: 1px solid black;">
      <th style="text-align:center; border: 1px solid black;">提醒关键词示例图</th>
      <th style="text-align:center; border: 1px solid black;">提醒命令示例图</th>
      <th style="text-align:center; border: 1px solid black;">提醒列表命令示例图</th>
      <th style="text-align:center; border: 1px solid black;">删除提醒命令示例图</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border: 1px solid black;">
      <td style="text-align:center; border: 1px solid black;">
        <img src="readme_images/提醒关键词示例.jpg" style="height:600px;" />
      </td>
      <td style="text-align:center; border: 1px solid black;">
        <img src="readme_images/提醒命令示例.jpg" style="height:600px;" />
      </td>
      <td style="text-align:center; border: 1px solid black;">
        <img src="readme_images/提醒列表命令示例.jpg" style="height:600px;" />
      </td>
      <td style="text-align:center; border: 1px solid black;">
        <img src="readme_images/删除提醒命令示例.jpg" style="height:600px;" />
      </td>
    </tr>
  </tbody>
</table>
